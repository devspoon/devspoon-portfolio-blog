# Total Report

작성일: 2026-08-09

## 결론

`docs/error`의 Sentry 이슈는 세 종류로 정리된다.

1. PHP/WordPress 탐색성 요청이 Django까지 도달했다.
2. 일별 접속 통계 테이블에 같은 날짜의 중복 row가 생겨 `get_or_create(created_at__date=today)`가 실패했다.
3. 포트폴리오 문의 폼에서 검증되지 않은 긴 입력과 외부 메일 서비스 크레딧/인증 문제가 섞여 Sentry 에러가 발생했다.

가장 먼저 적용할 대응은 nginx에서 `.php`, WordPress 경로, phpinfo 탐색 요청을 `444`로 끊는 것이다. 그 다음 Django 최상단 미들웨어에서 같은 패턴을 2차로 조기 차단해 통계 미들웨어, URL resolver, Sentry까지 불필요하게 흘러가지 않도록 한다.

## 우선순위

| 우선순위 | 작업 | 이유 |
| --- | --- | --- |
| P0 | nginx PHP/WordPress 스캔 차단 | 애플리케이션 비용과 Sentry 노이즈를 즉시 줄인다. |
| P0 | 통계 테이블 중복 데이터 정리 | 현재 중복 row가 존재하면 매 요청마다 `MultipleObjectsReturned`가 재발한다. |
| P1 | 통계 모델을 일자 단위 유니크 구조로 변경 | 중복 재발을 구조적으로 막는다. |
| P1 | 문의 폼 입력 검증 및 로그 저장 순서 개선 | `DataError`와 가짜 성공 로그를 막는다. |
| P1 | SendGrid 크레딧/키 상태 점검 및 메일 실패 처리 개선 | 외부 서비스 실패를 사용자 성공 처리와 분리한다. |
| P2 | Sentry 필터링/태그 정리 | 악성 스캔과 실제 장애를 분리해 관측 품질을 높인다. |

## 확인된 이슈별 요약

### PHP/WordPress 스캔 트래픽

- Sentry 문서:
  - `ConnectionHardwareStats.MultipleObjectsReturned.md`: `/wp.php`
  - `ConnectionMethodStats.MultipleObjectsReturned.md`: `/bbs/board.php`
  - 이메일 401 문서 breadcrumbs: `/public_html/phpinfo.php`, `/site/phpinfo.php`, `/wp-admin/phpinfo.php`, `/includes/phpinfo.php`
- 문제:
  - 서비스와 무관한 `.php`/WordPress 탐색 요청이 Django까지 도달했다.
  - 이 요청도 통계 미들웨어가 처리하면서 DB write와 Sentry 이벤트를 유발했다.
- 권장:
  - nginx `server` 블록에서 `return 444`로 즉시 차단한다.
  - Django에는 fallback 조기 차단 미들웨어를 통계 미들웨어보다 앞에 둔다.

### 통계 중복 row

- 관련 코드:
  - `custom_middlewares/middlewares/statistics.py`
  - `custom_middlewares/models.py`
- 문제:
  - `created_at`은 `DateTimeField(auto_now_add=True)`이고 일자 유니크 제약이 없다.
  - `get_or_create(created_at__date=today)`는 실제 생성 시 `created_at__date` 값을 넣을 수 없고, 동시 요청 또는 과거 로직으로 같은 날짜 row가 여러 개 생길 수 있다.
  - 중복이 한 번 생기면 이후 `get_or_create()`의 내부 `get()`이 계속 `MultipleObjectsReturned`를 발생시킨다.
- 권장:
  - `stat_date = DateField(unique=True)`를 추가해 일자 단위 집계키로 사용한다.
  - 기존 중복 row를 날짜별로 합산해 하나로 정리하는 data migration 또는 운영 스크립트를 먼저 실행한다.

### 문의 폼 DataError

- Sentry 문서: `DataError.md`
- 관련 코드:
  - `portfolio/views.py`
  - `portfolio/models.py`
  - `templates/portfolio/portfolio.html`
- 문제:
  - `GetInTouchLog.phone_number`는 `max_length=16`인데 Sentry 입력값은 랜덤 문자열로 16자를 초과한다.
  - 현재 뷰는 `number` 길이와 휴대폰 형식 검증을 저장 전에 명확히 수행하지 않는다.
  - `GetInTouchView.check_email_validation_with_dns()`의 예외 경로에서 `is_valid`가 초기화되지 않을 수 있다.
  - `GetInTouchView.post()` 하단에는 도달 불가능한 중복 코드가 여러 번 남아 있다.
- 권장:
  - `forms.Form` 또는 `ModelForm`으로 문의 입력 검증을 이동한다.
  - `phone_number`는 optional이면 빈 값 허용, 입력 시 길이/형식 검증을 엄격히 적용한다.
  - 저장은 메일 큐 등록/발송 결과 정책과 분리해 `state` 의미를 재정의한다.

### 이메일 401 / Maximum credits exceeded

- Sentry 문서:
  - `Error sending email to ['[email]']: HTTP Error 401: Unauthorized.md`
  - `Failed to send email, error: HTTP Error 401: Unauthorized, response body: ... Maximum credits exceeded ... .md`
- 관련 코드:
  - `utils/email/async_send_email.py`
  - `config/settings/base.py`
  - `config/settings/sub_settings/email/sendgrid.py`
- 문제:
  - SendGrid 또는 연결된 메일 백엔드가 인증/크레딧 문제로 실패하고 있다.
  - 현재 `send_mail()`은 스레드를 시작하고 즉시 반환하므로 뷰에서 실패 여부를 알 수 없다.
  - 문의 폼은 메일 실패 가능성과 무관하게 성공 메시지를 보여준다.
- 권장:
  - 운영 메일 벤더 상태와 과금/크레딧/키 권한을 즉시 확인한다.
  - 비동기 스레드 대신 Celery 작업 또는 동기 결과 반환 래퍼로 실패 상태를 추적한다.
  - 실패 이벤트에는 recipient 원문을 마스킹하고, 사용자에게는 접수/발송 상태를 분리해 안내한다.

## 승인 필요 사항

- nginx 설정에 `return 444` 정책을 적용할지, 또는 운영 표준상 `403`/`404`로 대체할지 결정해야 한다.
- 통계 테이블 중복 row 정리 시 날짜별 카운트를 합산할지, 최신 row만 보존할지 결정해야 한다. 권장은 합산이다.
- 문의 폼 전화번호 정책을 국내 휴대폰 형식만 허용할지, 국제 전화번호까지 허용할지 결정해야 한다.
- 메일 실패 시 사용자 메시지를 "접수 완료, 발송 지연"으로 바꿀지, 실패로 명확히 안내할지 결정해야 한다.

## 다음 작업

구현자는 [../plans/04-remediation-work-plan.md](../plans/04-remediation-work-plan.md)의 단계 순서대로 진행한다. nginx 반영은 앱 배포와 별도 운영 작업이므로, 적용 후 access log와 Sentry 발생량을 함께 확인한다.
