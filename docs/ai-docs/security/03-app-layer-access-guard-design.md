# App Layer Access Guard Design

상태: **구현 완료** — 2026-08-10

- 구현: `custom_middlewares/middlewares/access_guard.py`
- 등록: `config/settings/base.py`의 `MIDDLEWARE`, `SecurityMiddleware` 바로 뒤
- 테스트: `custom_middlewares/tests/test_access_guard.py`

아래 설계안과 실제 구현의 차이는 문서 끝의 "구현과의 차이"에 정리했다.

## 목표

nginx에서 놓친 비서비스 요청을 Django 애플리케이션 초입에서 2차로 차단한다. 이 방어선은 nginx의 대체물이 아니라 fallback이다.

## 중요한 전제

Django 애플리케이션은 nginx의 `return 444`처럼 TCP 연결을 즉시 drop할 수 없다. 앱 계층에서는 다음 중 하나를 선택한다.

- `HttpResponse(status=404)`: 스캐너에게 정보 노출이 적고 일반적이다.
- `HttpResponse(status=403)`: 차단 의도가 명확하지만 스캐너에게 정책 존재를 드러낸다.
- `SuspiciousOperation`: Django 보안 로그와 400 응답으로 연결된다. Sentry 노이즈가 생길 수 있다.

권장은 `404` 조기 반환이다. 실제 drop은 nginx에서 처리한다.

## 미들웨어 위치

`config/settings/base.py`의 `MIDDLEWARE`에서 통계 미들웨어보다 앞, 가능하면 `SecurityMiddleware` 바로 뒤에 둔다.

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "custom_middlewares.middlewares.access_guard.BlockSuspiciousPathMiddleware",
    ...
    "custom_middlewares.middlewares.statistics.ConnectionMethodStatsMiddleware",
    "custom_middlewares.middlewares.statistics.ConnectionHardwareStatsMiddleware",
]
```

이렇게 해야 차단 요청이 통계 DB write 경로에 들어가지 않는다.

## 설계안

신규 파일 후보:

- `custom_middlewares/middlewares/access_guard.py`

설정값 후보:

- `BLOCK_SUSPICIOUS_PATHS = True`
- `SUSPICIOUS_PATH_RESPONSE_STATUS = 404`
- `SUSPICIOUS_PATH_PATTERNS = [...]`

예상 구현:

```python
import re

from django.conf import settings
from django.http import HttpResponse


DEFAULT_SUSPICIOUS_PATH_PATTERNS = [
    r"(^|/)(wp-admin|wp-content|wp-includes)(/|$)",
    r"(^|/)(phpinfo|xmlrpc|wp-login|wp-config|wp-cron|wp-load|wp-mail|wp-settings|wp-signup|wp-trackback|wp)\.php$",
    r"\.php(?:/|$)",
]


class BlockSuspiciousPathMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        raw_patterns = getattr(
            settings,
            "SUSPICIOUS_PATH_PATTERNS",
            DEFAULT_SUSPICIOUS_PATH_PATTERNS,
        )
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in raw_patterns]
        self.enabled = getattr(settings, "BLOCK_SUSPICIOUS_PATHS", True)
        self.status = getattr(settings, "SUSPICIOUS_PATH_RESPONSE_STATUS", 404)

    def __call__(self, request):
        if self.enabled and self._is_suspicious_path(request.path_info):
            return HttpResponse(status=self.status)
        return self.get_response(request)

    def _is_suspicious_path(self, path):
        return any(pattern.search(path) for pattern in self.patterns)
```

## Host 검증과 도메인 무관 접근

Django의 `ALLOWED_HOSTS`는 이미 `config/settings/prod.py`에서 환경변수 기반으로 설정된다. Host 헤더가 허용되지 않으면 Django는 `DisallowedHost`를 발생시킨다.

추가 개선 방향:

- 운영 `ALLOWED_HOSTS_IP`에 실제 서비스 도메인과 필요한 내부 호스트만 둔다.
- IP 직접 접근을 nginx default server에서 먼저 차단한다.
- 앱 계층에서 별도 Host guard를 추가할 경우 `request.get_host()` 호출 자체가 `DisallowedHost`를 발생시킬 수 있으므로, Sentry 필터와 함께 설계한다.

권장 순서:

1. nginx default server로 미등록 Host를 `444` 처리한다.
2. Django `ALLOWED_HOSTS`를 최소화한다.
3. Sentry에서 `DisallowedHost`를 ignore하거나 낮은 레벨로 필터링한다.

## 통계 미들웨어와의 연계

차단 미들웨어가 들어가도 통계 미들웨어 자체는 다음 개선이 필요하다.

- `admin` 문자열 포함 여부가 아니라 `request.path_info.startswith("/admin/")` 같은 명확한 조건 사용
- static/media/healthcheck/sitemap/robots 처리 정책 정의
- 봇 user-agent를 통계에서 제외하거나 별도 컬럼으로 분리
- DB write 실패가 전체 요청 실패로 번지지 않도록 방어

## 테스트 계획

- `.php` 요청은 404 또는 설정 status를 반환한다.
- `.php` 요청 시 `ConnectionMethodStats`와 `ConnectionHardwareStats`가 증가하지 않는다.
- 정상 URL은 기존 응답을 유지한다.
- `BLOCK_SUSPICIOUS_PATHS=False`일 때 차단이 비활성화된다.

네 항목 모두 `custom_middlewares/tests/test_access_guard.py`에 구현됐다.
조기 차단과 일반 404를 구분하기 위해, 차단 응답은 본문이 비어 있다는 점(`response.content == b""`)까지 검증한다.

## 구현과의 차이

- 차단 패턴에 자격증명/설정 파일 유출 스캔을 추가했다: `(^|/)\.(env|git|aws|ssh)(/|$)`
- 차단 시 `blocked suspicious path` INFO 로그를 남긴다. 별도 metric 없이 차단량을 확인할 수 있다.
- "통계 미들웨어와의 연계"에 적은 개선 사항도 함께 반영했다.
  - `admin` 부분 문자열 대신 `STATS_EXCLUDED_PATH_PREFIXES` 기반 prefix 판정
  - static/media/silk/robots/sitemap 제외
  - 통계 DB 오류를 `DatabaseError`로 잡아 요청 실패로 번지지 않게 처리
  - 봇은 현행 유지. 하드웨어 통계에 이미 `bot` 컬럼이 있어 별도 분리가 필요 없다.

## Host 검증 처리 결과

문서의 권장 순서 중 앱 계층 몫은 적용했다.

- 별도 Host guard 미들웨어는 만들지 않았다. `request.get_host()` 호출 자체가 `DisallowedHost`를 발생시켜 얻는 것보다 잃는 게 많다.
- 대신 `config/settings/sub_settings/system/sentry.py`의 `before_send`에서 `DisallowedHost`를 버린다.
- nginx default server 차단과 `ALLOWED_HOSTS` 최소화는 운영 작업으로 남는다.
