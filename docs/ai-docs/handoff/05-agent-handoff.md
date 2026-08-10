# Agent Handoff

갱신일: 2026-08-10

## 현재 상태

- `docs/error`에 Sentry export 5개가 있다.
- `docs/error`는 현재 git 기준 미추적 상태로 보인다. 이번 작업에서 바꾸지 않았다.
- 계획서 Phase 1~5의 코드 작업이 끝났다. 테스트는 151 passed / 1 skipped이고 sqlite와 PostgreSQL 양쪽에서 통과한다.
- 남은 것은 운영 작업이다: nginx 차단 적용, 운영 DB 정리 실행, SendGrid 계정 점검.
- 결과 정리는 [../reports/06-implementation-report.md](../reports/06-implementation-report.md)에 있다.

## 주요 코드 위치

기존 위치:

- 통계 미들웨어: `custom_middlewares/middlewares/statistics.py`
- 통계 모델: `custom_middlewares/models.py`
- 통계 admin 등록: `home/admin/default_admin.py`, `custom_middlewares/admin/home_statistics_admin.py`
- 문의 모델: `portfolio/models.py`
- 문의 뷰: `portfolio/views.py`
- 문의 템플릿: `templates/portfolio/portfolio.html`
- 메일 스레드 발송: `utils/email/async_send_email.py`
- 공통 middleware 설정: `config/settings/base.py`
- 운영 `ALLOWED_HOSTS`: `config/settings/prod.py`

이번 작업에서 추가된 위치:

- 탐색성 경로 차단: `custom_middlewares/middlewares/access_guard.py`
- 통계 정리 명령: `custom_middlewares/management/commands/dedupe_connection_stats.py`
- 문의 폼: `portfolio/forms.py` (reCAPTCHA 포함)
- 전화번호 validator: `portfolio/validators.py`
- Sentry 이벤트 필터: `config/settings/sub_settings/system/sentry.py`
- 테스트: `custom_middlewares/tests/`, `portfolio/tests/`

## 확인 완료된 사항

핸드오프 시점에 미확인이던 항목들의 결과다.

1. 운영 nginx 설정 파일은 이 저장소에 없다. 여전히 배포 환경에서 별도로 작업해야 한다.
2. `migrations/`는 `.gitignore` 대상이라 저장소에 마이그레이션이 없다.
   그래서 중복 정리는 data migration이 아니라 management command로 만들었다.
3. `custom_middlewares.models`의 통계 모델은 `Meta.app_label = "home"`이라
   마이그레이션이 **`home/migrations/`**에 생성된다. `custom_middlewares`에는 생기지 않는다.
   `makemigrations --dry-run -v 2`와 실제 마이그레이션 리허설로 확인했다.
4. `GetInTouchView.post()`의 도달 불가능한 dead code 6블록을 제거했다.
5. `utils/email/async_send_email.py`에 결과를 반환하는 `send_mail_sync()`를 추가했고,
   문의 폼은 이 함수를 쓴다. 기존 스레드 방식 `send_mail()`은 `verify_email_mixins.py`용으로 유지된다.

새로 확인한 것:

6. 저장소에 `migrations/` 디렉터리가 없는 상태에서는 인자 없는 `makemigrations`가
   프로젝트 앱에 아무것도 만들지 않는다("No changes detected"). 최초 1회는 앱 이름을 명시해야 한다.

```bash
python manage.py makemigrations users blog board home portfolio custom_middlewares
```

7. `common/error/error_views.py`의 400/403/404/500 핸들러가 모두 HTTP 200을 반환하고 있었다. 함께 수정했다.
8. `config/settings/prod.py`가 `manage.py check`에서 `staticfiles.E002`로 실패하고 있었다.
   `check`는 모든 관리 명령 앞에서 실행되므로 prod 설정으로는 `migrate`도 정리 명령도 돌릴 수 없었다.
   `stage.py`와 같은 형태로 맞춰 해결했다. 네 설정 모두 `check` 오류가 없다.

## 결정된 항목

핸드오프의 "열려 있는 결정"에 대한 답이다.

| 항목 | 결정 |
| --- | --- |
| nginx 차단 응답 | `444` 유지. 앱 계층은 `404` |
| 전화번호 입력 정책 | 선택 입력, 값이 있으면 국내 휴대폰 형식만 허용 |
| 통계의 봇 처리 | 현행 유지 (하드웨어 통계에 `bot` 컬럼이 이미 있다) |
| `GetInTouchLog.state` 의미 | 문의 접수 성공 여부. 메일 결과는 신규 `status` |
| 메일 비동기 처리 | 문의 폼은 동기 발송으로 전환. Celery 이관은 후속 과제 |

## 새로 추가된 설정값

`config/settings/base.py`에 있다.

| 설정 | 기본값 | 용도 |
| --- | --- | --- |
| `BLOCK_SUSPICIOUS_PATHS` | `True` | 탐색성 경로 차단 on/off |
| `SUSPICIOUS_PATH_RESPONSE_STATUS` | `404` | 차단 응답 status |
| `SUSPICIOUS_PATH_PATTERNS` | 기본 패턴 목록 | 차단 정규식 |
| `SUSPICIOUS_PATH_LOG_LEVEL` | `"INFO"` | 차단 로그 레벨. 기본값은 common 로거(WARNING)에 걸려 기록되지 않는다 |
| `STATS_EXCLUDED_PATH_PREFIXES` | admin/static/media/silk/robots/sitemap | 통계 제외 경로 |
| `EMAIL_DNS_VALIDATION` | `True` (test는 `False`) | 문의 폼 이메일 DNS 검증 |
| `EMAIL_DNS_VALIDATION_TIMEOUT` | `10` | DNS 조회 타임아웃(초) |
| `CONTACT_FORM_CAPTCHA` | `False` (prod/stage는 `True`) | 문의 폼 reCAPTCHA |

## 검증 명령

```bash
python manage.py check --settings=config.settings.dev
pytest
pytest -m middlewares
pytest -m portfolio
```

로컬 실행에는 `.env`와 Redis가 필요하다.
`config/settings/test.py`는 import 시점에 `get_redis_connection()`을 호출하므로 Redis가 떠 있어야 한다.
필요한 환경변수 목록은 `.github/workflows/testing.yml`의 "Add environment variables to .env" 단계를 참고한다.

DB는 sqlite를 쓰고 `pytest.ini`의 `--no-migrations`로 모델에서 직접 테이블을 만든다.

## 다음 담당자가 할 일

1. nginx 차단 location 적용 ([../security/02-nginx-php-scan-blocking.md](../security/02-nginx-php-scan-blocking.md))
2. 운영 DB 백업 후 마이그레이션과 `dedupe_connection_stats` 실행
   ([../reports/06-implementation-report.md](../reports/06-implementation-report.md)의 "운영 배포 절차")
3. SendGrid API key / sender 인증 / 크레딧 점검
4. 배포 후 Sentry에서 `MultipleObjectsReturned`, `DataError`, PHP 스캔 이벤트가 사라졌는지 확인
