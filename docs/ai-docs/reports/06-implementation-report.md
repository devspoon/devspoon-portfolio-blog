# Implementation Report

작성일: 2026-08-10
브랜치: `docs/sentry-error-remediation-plan`
기준 문서: [../plans/04-remediation-work-plan.md](../plans/04-remediation-work-plan.md)

## 요약

[04-remediation-work-plan.md](../plans/04-remediation-work-plan.md)의 Phase 1~5를 코드로 구현했다.
Phase 0(nginx)은 이 저장소에 설정 파일이 없어 운영 작업으로 남는다.

테스트는 `pytest` 기준 **151 passed, 1 skipped**이다. sqlite와 운영과 같은 PostgreSQL 양쪽에서 통과한다.
작업 시작 시점의 기준선은 9 passed, 1 skipped였으므로 142건이 새로 추가되었다.
이 브랜치가 변경한 모듈은 모두 라인 커버리지 100%다.
skip 1건은 이 작업과 무관한 기존 항목(`home.tests.test_home_html.test_home`)이다.

`dev`, `test`, `stage`, `prod` 네 설정 모두 `manage.py check`에서 오류가 없다.

## 확정된 결정

계획서 "열려 있는 결정"과 "승인 필요 사항"에 대한 답이다.

| 항목 | 결정 |
| --- | --- |
| 앱 계층 차단 응답 | `404`. `SUSPICIOUS_PATH_RESPONSE_STATUS`로 변경 가능 |
| nginx 차단 응답 | `444` 유지 (운영 적용 시 판단) |
| 통계 중복 정리 방식 | 날짜별 **합산**. 최신 row만 보존하지 않는다 |
| 통계 마이그레이션 | migration 파일 대신 management command로 정리 |
| 전화번호 정책 | 선택 입력, 값이 있으면 국내 휴대폰 형식만 허용 |
| 메일 비동기 처리 | 문의 폼은 **동기 발송**으로 전환, 결과를 상태로 기록 |
| `GetInTouchLog.state` 의미 | 접수 성공 여부로 확정. 발송 결과는 신규 `status`로 분리 |
| 통계의 봇 처리 | 현행 유지. 하드웨어 통계에 이미 `bot` 컬럼이 있다 |

## Phase별 구현 내용

### Phase 0: 운영 차단 (미완료 — 운영 작업)

이 저장소에는 nginx 설정 파일이 없다.
[../security/02-nginx-php-scan-blocking.md](../security/02-nginx-php-scan-blocking.md)의 location 블록을 운영 서버에 직접 적용해야 한다.
앱 계층 차단(Phase 1)이 이미 동작하므로 서비스 안전성 문제는 없고, 남은 이득은 gunicorn까지 도달하는 트래픽량 감소다.

### Phase 1: Django 2차 차단 미들웨어 (완료)

신규 `custom_middlewares/middlewares/access_guard.py`의 `BlockSuspiciousPathMiddleware`.

- `config/settings/base.py`의 `MIDDLEWARE`에서 `SecurityMiddleware` 바로 뒤, 통계 미들웨어보다 앞에 위치한다.
- 차단 시 본문 없는 `404`를 조기 반환하므로 URL resolver와 통계 DB write 경로를 타지 않는다.
- 설정값: `BLOCK_SUSPICIOUS_PATHS`, `SUSPICIOUS_PATH_RESPONSE_STATUS`, `SUSPICIOUS_PATH_PATTERNS`.
- 설계 문서 대비 추가한 패턴: `.env`, `.git`, `.aws`, `.ssh` 유출 스캔.

### Phase 2: 통계 중복 정리 및 모델 개선 (완료)

`custom_middlewares/models.py`:

- `DailyStatsMixin`을 도입하고 `stat_date = DateField(unique=True)`를 집계키로 추가했다.
- `ordering`을 `-created_at`에서 `-stat_date`로 바꿨다.
- 각 모델에 `COUNTER_FIELDS`를 정의해 정리 스크립트가 카운터 컬럼을 알 수 있게 했다.

`custom_middlewares/middlewares/statistics.py`:

- `get_or_create(created_at__date=today)`를 버리고 `increment_daily_counter()`로 교체했다.
  UPDATE → (없으면) INSERT → (경합 시) UPDATE 순서로 처리한다.
  UPDATE 한 문장이 원자적이라 `select_for_update` 잠금이 필요 없다.
- 동시 생성 경합은 유니크 제약과 `IntegrityError` 재시도로 처리한다.
- admin 판별을 `"admin" not in request.path`에서 `path_info.startswith()` 기반 prefix 목록으로 바꿨다.
  설정값은 `STATS_EXCLUDED_PATH_PREFIXES`이고 static/media/silk/robots/sitemap을 포함한다.
- 통계 DB 오류가 사용자 요청 실패로 번지지 않도록 `DatabaseError`를 잡아 경고 로그만 남긴다.

`custom_middlewares/management/commands/dedupe_connection_stats.py`:

- 날짜별 중복 row의 카운트를 합산해 1개로 병합하고 `stat_date`를 backfill한다.
- `--dry-run`을 지원하고, 여러 번 실행해도 결과가 같다.

`custom_middlewares/admin/home_statistics_admin.py`:

- `created_at__day=...`은 '일(day of month)'만 비교해 다른 달 row까지 섞였다. `stat_date=오늘`로 교체했다.

#### `stat_date`를 nullable로 둔 이유

이 프로젝트는 `.gitignore`에 `migrations/`가 있어 migration 파일을 저장소에 두지 않는다.
기존 운영 테이블에 not-null unique 컬럼을 한 번에 추가하면 모든 기존 row가 같은 기본값을 받아 유니크 제약에 걸린다.
nullable로 추가하면 기존 row는 전부 NULL이 되고(유니크 제약은 NULL을 비교하지 않는다),
이어서 `dedupe_connection_stats`가 합산과 backfill을 수행한다. 마이그레이션 1회로 끝난다.

계획서는 `unique=True, db_index=True`를 제시했으나 `db_index`는 생략했다.
Django는 `unique=True`일 때 별도 인덱스를 만들지 않으므로 중복 지정이다.

### Phase 3: 문의 폼 검증 개선 (완료)

신규 `portfolio/forms.py`의 `GetInTouchForm`, 신규 `portfolio/validators.py`.

| 필드 | 정책 |
| --- | --- |
| `name` | 필수, trim, 최대 300자 |
| `emailfrom` | 필수, `EmailField`, 최대 128자, `test` 포함 도메인 거부, DNS MX 검증 |
| `number` | 선택, 최대 16자, 값이 있으면 국내 휴대폰 형식 |
| `subject` | 필수, trim, 최대 300자 |
| `message` | 필수, trim, 최대 5000자 |

- `GetInTouchView.post()`를 form 기반으로 재작성했다. 첫 `return` 뒤에 6번 반복되던 도달 불가능한 저장 코드를 제거했다(뷰 172줄 → 66줄).
- `check_email_validation_with_dns()`의 `is_valid` 미초기화 문제는 로직을 `GetInTouchForm.clean_emailfrom()`으로 옮기며 해소했다.
- DNS 예외를 두 갈래로 나눴다. `DNSTimeoutError`/`DNSConfigurationError`/`NoNameserverError`는 '검증 불가'로 보고 통과시키고,
  `NoMXError` 등 나머지는 '잘못된 주소'로 보고 거부한다. 이전 구현은 DNS 타임아웃도 잘못된 주소로 처리했다.
- `EMAIL_DNS_VALIDATION` 설정으로 DNS 검증을 끌 수 있고, 테스트 환경에서는 꺼 둔다.
- 수신자는 hidden input `emailto`가 아니라 `settings.DEFAULT_FROM_EMAIL`로 고정된다는 점을 테스트로 고정했다.
- `templates/portfolio/portfolio.html`의 입력 필드에 서버 정책과 같은 `maxlength`와 `required`를 추가했다.

#### reCAPTCHA

`django-recaptcha`를 문의 폼에 붙였다. `CONTACT_FORM_CAPTCHA` 설정으로 켜고 끄며, 기본값은 `False`다.
`prod`와 `stage`에서만 켠다.

- 필드는 클래스 속성이 아니라 `GetInTouchForm.__init__()`에서 만든다.
  클래스 속성으로 두면 import 시점에 RECAPTCHA 키를 요구해서, 키가 없는 환경에서 폼을 쓸 수 없다.
- 검증이 Google API 호출을 동반하므로 테스트에서는 꺼 두고, 켠 경로는 `captcha.fields.client.submit`을 mock해서 검증한다.
- `PortfolioView`는 폼 인스턴스를 redis 캐시 저장이 끝난 뒤에 context에 넣는다.
  캐시에 들어가면 모든 방문자가 같은 인스턴스를 보게 된다.
- 템플릿은 `{% if get_in_touch_form.captcha %}`로 감싸 꺼진 환경에서는 아무것도 렌더하지 않는다.

**운영 적용 시 주의.** `RECAPTCHA_PUBLIC_KEY` / `RECAPTCHA_PRIVATE_KEY`의 기본값은 Google 테스트 키다.
테스트 키를 그대로 두면 `manage.py check`가 `captcha.recaptcha_test_key_error`로 실패한다.
이는 이 작업 이전부터 있던 동작이고, 실제 키를 넣지 않은 채 배포되는 것을 막아주는 안전장치다.

### Phase 4: 메일 발송 실패 처리 (완료)

`utils/email/async_send_email.py`:

- `send_mail_sync()`를 추가했다. 동기로 발송하고 성공 여부를 `bool`로 반환한다.
- 기존 스레드 방식 `send_mail()`은 그대로 두되 내부에서 `send_mail_sync()`를 호출하도록 정리했다.
  `utils/email/verify_email_mixins.py`가 계속 사용한다.
- `mask_email()` / `mask_recipients()`로 로그와 Sentry에서 수신자 주소를 마스킹한다. (`hong.gildong@gmail.com` → `h***g@gmail.com`)

`portfolio/models.py`:

- `GetInTouchLog.status`(`received`/`queued`/`sent`/`failed`)를 추가했다.
- `state`는 '문의 접수 성공 여부'로 의미를 확정했고, 메일 발송 결과는 `status`가 담는다.
- `phone_number`의 인라인 정규식을 `portfolio/validators.py`의 공용 validator로 교체했다.
  기존 정규식 `[0|1|6|7|8|9]`은 문자 클래스에 `|`가 그대로 들어가 있어 `01|-1234-5678` 같은 입력을 통과시켰다.

`portfolio/views.py`:

- 문의를 **먼저 저장**하고 그 뒤에 메일을 보낸다. 메일 벤더 장애로 문의가 유실되지 않는다.
- 발송 결과에 따라 `status`를 `sent`/`failed`로 갱신한다.
- 발송 실패 시 성공 메시지 대신 "접수 완료, 발송 지연" 경고 메시지를 보여준다.

`portfolio/admin.py`의 `GetInTouchLogAdmin`에 `status`를 list_display와 list_filter에 추가했다.

**SendGrid 계정 상태 점검은 코드 작업이 아니다.** API key 유효성, sender/domain 인증, 크레딧 한도는 운영자가 직접 확인해야 한다.

### Phase 5: 관측 및 회귀 방지 (완료)

신규 `config/settings/sub_settings/system/sentry.py`:

- `before_send` 훅으로 스캐너 노이즈를 버린다.
- 버리는 대상: `Http404`, `DisallowedHost`, `SuspiciousOperation` 예외와 `.php`/`wp-*`/`.env` 계열 URL에서 난 이벤트.
- `config/settings/prod.py`와 `config/settings/stage.py`의 `sentry_sdk.init()`에 연결했다.

차단량 집계는 별도 metric을 두지 않고 nginx access log와 미들웨어 로그(`blocked suspicious path`)로 확인한다.

단, 기본 설정에서는 이 로그가 **남지 않는다.** 차단은 정상 동작이라 로그 레벨이 INFO인데
`COMMON_LOGGER`("common") 로거가 WARNING이라 걸러진다.
Django 로그로 차단량을 집계하려면 `SUSPICIOUS_PATH_LOG_LEVEL = "WARNING"`으로 올린다.
E2E에서 올렸을 때 실제로 기록되는 것을 확인했다.

테스트는 `pytest.ini`에 `portfolio`, `middlewares` 마커를 추가해 CI에서 자동 수집된다.

## 계획 외 추가 수정

### 커스텀 에러 페이지가 HTTP 200을 반환하던 문제

`common/error/error_views.py`의 400/403/404/500 핸들러가 모두 다음 형태였다.

```python
response = HttpResponse()
response.status_code = 404      # 이 응답은 버려진다
return render(request, "errors/error.html", context=context)   # 200으로 나간다
```

`render()`가 새 응답을 만들기 때문에 위에서 설정한 status_code는 사용되지 않았다.
결과적으로 존재하지 않는 URL이 **HTTP 200**으로 응답했다. 스캐너에게는 모든 경로가 유효해 보이고, 검색엔진과 모니터링도 오탐한다.
`render(..., status=<code>)`로 수정했다.

기존 테스트 `home.tests.test_error.test_error_404`는 본문의 "404 Error" 문자열만 검사해 이 문제를 잡지 못했다.

### prod 설정의 `staticfiles.E002`

`config/settings/prod.py`가 `STATICFILES_DIRS`에 `STATIC_ROOT`와 같은 경로를 넣고 있어 `manage.py check`가 실패했다.
`check`는 모든 관리 명령 앞에서 실행되므로, prod 설정으로는 `migrate`도 `dedupe_connection_stats`도 돌릴 수 없었다.

`stage.py`는 이미 같은 이유로 `STATICFILES_DIRS`를 주석 처리하고
"static 파일을 한 곳에 모아서 서비스 할 경우 상위 STATICFILES_DIRS 변수는 불필요함"이라고 적어 두었다.
prod도 같은 형태로 맞췄다. static은 `STATIC_ROOT`(`ROOT_DIR/static`) 한 곳에서 서비스하고,
이 디렉터리에는 이미 collectstatic 결과물(`admin/`, `silk/`, `summernote/` 등)이 들어 있다.

### 에러 페이지 버그가 실제 장애를 가리고 있었다

E2E 중에 `/users/login/`이 `SocialApp.DoesNotExist`로 크래시하는 것을 발견했다.
템플릿이 google/kakao/naver provider를 참조하는데 해당 `SocialApp` row가 없어서다.
이 브랜치는 `users/`를 건드리지 않았으므로 기존 문제다.

중요한 것은 이 페이지가 **수정 전에는 HTTP 200으로 응답했다**는 점이다.

| | 반환 status |
| --- | --- |
| 수정 전(`c9b0eae`) | **200** (본문에는 500이라고 적혀 있음) |
| 수정 후 | **500** |

즉 에러 페이지 버그가 실제 서버 오류를 가리고 있었다.
배포하면 그동안 200으로 집계되던 실패가 제대로 5xx로 드러난다.
**모니터링에 5xx가 갑자기 나타나더라도 새로 생긴 장애가 아니라 원래 있던 장애가 보이기 시작한 것일 수 있다.**
운영의 `/users/login/`도 같은 상태인지 확인이 필요하다.

### 로그에서 상세가 사라지던 문제

PII 마스킹을 넣으면서 수신자와 오류 원인을 `extra=`로만 넘겼는데,
프로젝트의 로그 포맷터는 `extra` 필드를 렌더하지 않는다.
그 결과 파일 로그에는 `Error sending email`만 남고 **어느 주소로 왜 실패했는지가 사라졌다.**
원래 코드보다 운영성이 나빠진 회귀였고 E2E에서 발견했다.

마스킹된 값과 오류를 메시지 본문에 넣고 `extra`는 구조화 소비자(Sentry)용으로 유지하도록 고쳤다.

```
ERROR [async_send_email.py:...] Error sending email to ['a***n@devspoon.com']: [Errno 111] Connection refused
```

같은 이유로 `access_guard`, `statistics`, `forms`의 로그도 함께 고쳤다.

## 검증

### 테스트

```
151 passed, 1 skipped        # sqlite
151 passed, 1 skipped        # postgresql 16
```

새로 추가한 테스트 파일:

| 파일 | 대상 |
| --- | --- |
| `custom_middlewares/tests/test_access_guard.py` | 탐색성 경로 차단, 통계 미접촉, 설정 토글 |
| `custom_middlewares/tests/test_statistics.py` | 집계 원자성, 유니크 제약, 경합 복구, 제외 경로 |
| `custom_middlewares/tests/test_dedupe_command.py` | 합산, 날짜 분리, backfill, 멱등성, dry-run |
| `custom_middlewares/tests/test_sentry_filter.py` | 노이즈 이벤트 폐기, 실제 오류 보존 |
| `portfolio/tests/test_get_in_touch_form.py` | 입력 정책, 전화번호 길이/형식, DNS 예외 분기 |
| `portfolio/tests/test_get_in_touch_view.py` | 접수/발송 분리, DataError 재발 방지, 수신자 고정 |
| `portfolio/tests/test_get_in_touch_captcha.py` | captcha 토글, 위젯 렌더, 검증 성공/실패 |
| `portfolio/tests/test_email_sending.py` | 발송 결과 반환, PII 마스킹 |

기존 `custom_middlewares/tests.py`와 `portfolio/tests.py`는 내용 없는 스텁이라 같은 이름의 패키지로 대체했다.

### 마이그레이션 리허설

실제 운영 업그레이드 순서를 재현해 검증했다. sqlite와 **운영과 같은 PostgreSQL 16** 양쪽에서 수행했다.

1. 변경 전(HEAD) 모델로 스키마를 만들고
2. 같은 날짜 중복 row를 심고 (`2026-08-05` 2건, `2026-08-06` 3건)
3. 신규 코드로 `makemigrations` / `migrate`를 적용한 뒤
4. `dedupe_connection_stats`를 실행했다.

결과:

- 마이그레이션이 중복 row가 있는 상태에서 오류 없이 적용됐다.
- 날짜별 1 row로 병합됐고 카운트가 정확히 합산됐다. (`2026-08-05`: win 10+7 = 17)
- DB 레벨 유니크 제약이 실제로 동작한다. (중복 INSERT 시 `UNIQUE constraint failed`)
- 두 번째 실행은 아무것도 바꾸지 않았다.
- PostgreSQL에서 `stat_date`에 **NULL을 여러 개 넣을 수 있음**을 직접 확인했다.
  `stat_date`를 nullable로 두고 마이그레이션 1회로 끝내는 설계의 근거다.

전체 테스트도 두 엔진에서 각각 통과한다(151 passed / 1 skipped).

### 실제 서버 E2E

`runserver`를 띄우고 PostgreSQL에 붙여 HTTP로 직접 확인했다.

| 시나리오 | 결과 |
| --- | --- |
| `/wp.php`, `/site/phpinfo.php`, `/bbs/board.php?...`, `/wp-admin/`, `/.env`, `/xmlrpc.php` | 전부 404, 본문 **0바이트** |
| 오탈자 URL(`/no-such-page`) | 404, 본문 15,920바이트 (에러 페이지 정상 렌더) |
| 메인 페이지 `/` | 200. sqlite에서 막혀 skip되던 페이지가 운영 엔진에서는 정상이다 |
| 16자 초과 전화번호 제출 | 302 redirect, **DB row 생성 안 됨** (DataError 재발 없음) |
| 정상 문의 제출 | 저장 + `status=sent` + 메일 파일 생성, 수신자는 `DEFAULT_FROM_EMAIL` |
| 메일 벤더 장애(연결 거부) 재현 | 문의는 저장되고 `status=failed`. 사용자에겐 지연 안내 |
| captcha ON | `g-recaptcha` 위젯과 api.js 렌더, captcha 없는 제출은 저장되지 않음 |
| `/robots.txt`, `/admin/home/`, 차단 경로 요청 | 통계 카운터 변화 없음 |
| 로그 | 수신자가 `['a***n@devspoon.com']`로 마스킹되고 원문 노출 0건 |

### 확인된 마이그레이션 동작

핸드오프 문서의 미확인 항목에 대한 답이다.

- 통계 모델은 `Meta.app_label = "home"` 때문에 마이그레이션이 **`home/migrations/`**에 생성된다. `custom_middlewares`에는 마이그레이션이 생기지 않는다.
- 저장소에 `migrations/` 디렉터리가 없는 상태에서 `python manage.py makemigrations`를 인자 없이 실행하면 **"No changes detected"만 나오고 아무것도 만들지 않는다.**
  Django는 migrations 패키지가 없는 앱을 인자 없는 makemigrations 대상에서 제외한다. 최초 1회는 앱 이름을 명시해야 한다.

```bash
python manage.py makemigrations users blog board home portfolio custom_middlewares
```

  `.github/workflows/testing.yml`의 `python manage.py makemigrations`도 같은 이유로 프로젝트 앱에는 사실상 아무 동작을 하지 않는다.
  테스트는 `pytest.ini`의 `--no-migrations` 덕분에 모델에서 직접 테이블을 만들어 통과한다.

## 운영 배포 절차

순서를 지켜야 한다.

```bash
# 0. 운영 DB 백업
# 1. nginx 차단 적용 (security/02 문서)
nginx -t && nginx -s reload

# 2. 코드 배포 후 마이그레이션 생성/적용
python manage.py makemigrations home portfolio --settings=config.settings.prod
python manage.py migrate --settings=config.settings.prod

# 3. 중복 현황 확인
python manage.py dedupe_connection_stats --dry-run --settings=config.settings.prod

# 4. 정리 실행
python manage.py dedupe_connection_stats --settings=config.settings.prod

# 5. 확인
#    - admin 통계 화면이 정상 동작하는지
#    - Sentry에 MultipleObjectsReturned가 더 오지 않는지
#    - gunicorn access log에 .php 요청이 사라졌는지
```

`config/settings/prod.py`의 `staticfiles.E002`(`STATICFILES_DIRS`가 `STATIC_ROOT`를 포함)는 함께 정리했다.
`stage.py`가 이미 같은 이유로 `STATICFILES_DIRS`를 주석 처리해 두었기에 prod도 같은 형태로 맞췄다.
static 파일은 `STATIC_ROOT`(`ROOT_DIR/static`) 한 곳에서 서비스하며, 이 디렉터리에는 이미 collectstatic 결과물이 들어 있다.
이제 `--skip-checks` 없이 prod 설정으로 위 명령을 실행할 수 있다.

## 남은 작업

| 항목 | 담당 | 비고 |
| --- | --- | --- |
| nginx 차단 location 적용 | 운영자 | Phase 0 |
| SendGrid API key / sender 인증 / 크레딧 점검 | 운영자 | Phase 4의 근본 원인 |
| 운영 DB 백업 후 dedupe 실행 | 운영자 | 위 배포 절차 |
| RECAPTCHA 실제 키 설정 | 운영자 | 테스트 키면 `check`가 실패한다 |
| 메일 발송의 Celery 이관 | 후속 | 아래 참고 |

### 동기 발송의 트레이드오프

문의 폼 메일을 동기로 보내므로 발송 결과를 정확히 알 수 있는 대신, 메일 벤더 응답이 느리면 그만큼 요청이 길어진다.
SendGrid 백엔드는 Django의 `EMAIL_TIMEOUT`을 따르지 않으므로 타임아웃을 앱에서 강제할 수 없다.

문의량이 늘거나 응답 지연이 문제가 되면 Celery task로 이관한다.
`GetInTouchLog.status`에 `queued`를 이미 정의해 두었으므로, 접수 시 `queued`로 저장하고 task 완료 시 `sent`/`failed`로 갱신하면 된다.
