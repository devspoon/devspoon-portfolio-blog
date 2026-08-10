# Sentry Error Review

갱신일: 2026-08-10

> 이 문서는 조사 시점의 원인 분석이다. 각 이슈의 처리 결과는 문서 끝의 "처리 결과"와
> [../reports/06-implementation-report.md](../reports/06-implementation-report.md)에 있다.

## 조사 범위

검토 대상은 `docs/error`의 5개 Sentry export 문서와 현재 Django 코드다.

## PYTHON-DJANGO-7H: ConnectionHardwareStats.MultipleObjectsReturned

- 파일: `docs/error/ConnectionHardwareStats.MultipleObjectsReturned.md`
- 발생일: 2026-08-05 23:32:04 UTC
- 요청: `GET /wp.php`
- 사용자 IP: `20.100.178.111`
- 관련 코드: `custom_middlewares/middlewares/statistics.py`

### 원인

`ConnectionHardwareStatsMiddleware`가 모든 비-admin 요청에서 일별 하드웨어 통계를 갱신한다. 현재 로직은 다음 형태다.

```python
ConnectionHardwareStats.objects.select_for_update().get_or_create(
    created_at__date=today
)
```

하지만 `created_at`은 자동 생성 datetime이고, 모델에는 일자 단위 유니크 키가 없다. 이미 같은 날짜 row가 2개 존재하는 상태에서 `get_or_create()` 내부 `get()`이 `MultipleObjectsReturned`를 발생시켰다.

### 영향

- PHP 스캔 요청 하나도 DB write 경로를 탄다.
- 같은 날짜 중복 row가 남아 있으면 정상 사용자 요청에서도 계속 재발할 수 있다.
- 통계 미들웨어가 URL 처리보다 앞서 실행되므로 404가 될 요청도 통계 DB를 건드린다.

### 해결 방향

- nginx에서 `/wp.php`, `.php` 요청을 우선 차단한다.
- Django 조기 차단 미들웨어를 통계 미들웨어보다 앞에 둔다.
- 통계 모델에 `stat_date` 또는 동등한 일자 집계키를 추가하고 유니크 제약을 둔다.
- 기존 중복 데이터를 날짜별로 합산 정리한다.

## PYTHON-DJANGO-7G: ConnectionMethodStats.MultipleObjectsReturned

- 파일: `docs/error/ConnectionMethodStats.MultipleObjectsReturned.md`
- 발생일: 2026-08-05 23:37:09 UTC
- 요청: `GET /bbs/board.php?bo_table=free&wr_id=1718`
- user-agent: `ClaudeBot/1.0`
- 관련 코드: `custom_middlewares/middlewares/statistics.py`

### 원인

하드웨어 통계와 같은 구조적 문제다. `ConnectionMethodStats` 역시 `created_at__date=today`로 조회하지만 날짜별 유니크 제약이 없다.

### 추가 관찰

- `/bbs/board.php`는 그누보드/게시판 계열 탐색성 URL로 보이며 현재 Django 서비스 URL과 무관하다.
- `ConnectionMethodStatsMiddleware.__call__()`는 `admin` 문자열만 제외하고 모든 user-agent 요청을 집계한다.
- 봇 요청도 운영체제 `oth`로 분류되어 실제 사용자 통계를 왜곡할 수 있다.

### 해결 방향

- 통계 집계 대상에서 차단 요청, 정적 파일, 헬스체크, 봇을 분리할지 정책화한다.
- 통계 갱신은 `update_or_create(stat_date=today, defaults=...)`보다 `filter(stat_date=today).update(...)` 후 없으면 생성하는 패턴 또는 DB upsert를 고려한다.
- 동시성은 DB 유니크 제약으로 최종 보장한다.

## PYTHON-DJANGO-7B: DataError value too long for type character varying(16)

- 파일: `docs/error/DataError.md`
- 발생일: 2026-07-12 11:28:03 UTC
- 요청: `POST /portfolio/mail`
- 사용자 IP: `185.220.101.168`
- 관련 코드:
  - `portfolio/views.py`
  - `portfolio/models.py`

### 원인

`GetInTouchLog.phone_number`는 `max_length=16`이고 RegexValidator도 정의되어 있다. 하지만 현재 뷰는 `number = request.POST.get("number", "")` 후 저장 전 `full_clean()` 또는 form validation을 실행하지 않는다. 결과적으로 16자를 초과한 랜덤 문자열이 DB insert까지 도달했다.

Sentry 변수의 `params`에는 다음처럼 무작위 입력이 포함되어 있다.

- `name`: 랜덤 문자열
- `email`: Gmail 주소
- `phone_number`: 16자 초과 랜덤 문자열
- `subject`: 랜덤 문자열
- `message`: 랜덤 문자열

정상 문의라기보다 폼 스팸/자동화 요청에 가깝다.

### 추가 문제

- `check_email_validation_with_dns()`는 예외 경로에서 `is_valid`가 정의되지 않은 채 반환될 수 있다.
- `post()` 하단에는 첫 번째 `return redirect(...)` 이후 도달 불가능한 중복 저장 코드가 반복된다.
- `emailto` hidden input은 읽지만 실제 발송 대상은 `settings.DEFAULT_FROM_EMAIL`로 고정되어 있다.
- 메일 전송 실패와 로그 저장 성공 여부가 분리되어 있지 않다.

### 해결 방향

- 문의 폼을 `forms.Form` 또는 `ModelForm`으로 전환한다.
- `name`, `subject`, `message` 길이 제한과 strip 처리를 추가한다.
- `phone_number`는 optional 입력으로 두되, 값이 있으면 모델과 동일한 validator를 뷰 계층에서 실행한다.
- 모델 저장 전 `form.is_valid()` 또는 `model.full_clean()`을 강제한다.
- 중복 dead code를 제거한다.

## PYTHON-DJANGO-7C / 7D: Email 401 Unauthorized

- 파일:
  - `docs/error/Error sending email to ['[email]']: HTTP Error 401: Unauthorized.md`
  - `docs/error/Failed to send email, error: HTTP Error 401: Unauthorized, response body: ... Maximum credits exceeded ... .md`
- 발생일: 2026-07-12 11:28:05 UTC
- 관련 코드:
  - `utils/email/async_send_email.py`
  - `config/settings/base.py`
  - `config/settings/sub_settings/email/sendgrid.py`

### 원인

메일 백엔드가 SendGrid로 설정되어 있고, Sentry 메시지에 `Maximum credits exceeded`가 포함되어 있다. 이는 코드 예외라기보다 외부 메일 서비스의 계정/크레딧/권한 상태 문제다.

### 코드상 문제

`utils/email/async_send_email.py`의 `send_mail()`은 스레드를 시작하고 종료한다. 스레드 내부 예외는 logger에만 남으며 호출자는 성공/실패를 알 수 없다.

```python
EmailThread(...).start()
```

따라서 `GetInTouchView.post()`는 메일 실패 여부와 무관하게 `messages.success()`를 반환할 수 있다.

### 해결 방향

- 운영 환경의 SendGrid API key, sender 인증, 크레딧/과금 상태를 점검한다.
- 메일 발송을 Celery task로 이관하고 task 상태를 기록하거나, 최소한 동기 발송 옵션을 둔다.
- 사용자-facing 메시지는 "문의 접수"와 "메일 발송 성공"을 분리한다.
- Sentry 로그에서 이메일 주소 등 PII를 마스킹한다.

## 공통 리스크

- 현재 `docs/error` 자체가 git 미추적 상태다. 문서화 및 구현 전 커밋 범위를 명확히 해야 한다.
- 운영 DB에 이미 중복 데이터가 있으므로 코드만 수정하면 마이그레이션이 실패하거나 중복 문제가 남을 수 있다.
- nginx 차단 없이 앱 코드만 수정하면 불필요한 요청량과 Sentry 노이즈가 계속 발생한다.

## 처리 결과 (2026-08-10)

| 이슈 | 처리 | 근거 |
| --- | --- | --- |
| PYTHON-DJANGO-7H `ConnectionHardwareStats.MultipleObjectsReturned` | 해결 | `stat_date` 유니크 제약 + `increment_daily_counter()` |
| PYTHON-DJANGO-7G `ConnectionMethodStats.MultipleObjectsReturned` | 해결 | 위와 동일 |
| PYTHON-DJANGO-7B `DataError value too long for varchar(16)` | 해결 | `GetInTouchForm`이 저장 전에 길이/형식을 거부 |
| PYTHON-DJANGO-7C / 7D `Email 401 Unauthorized` | 코드 측면 해결 | 발송 결과를 `status`로 기록하고 사용자 안내를 분리. 계정/크레딧 점검은 운영 작업 |

원인 분석 중 다음 두 가지는 실제 구현에서 수정됐다.

- `check_email_validation_with_dns()`의 `is_valid` 미초기화: 로직을 `GetInTouchForm.clean_emailfrom()`으로 옮기며 해소했다.
  더불어 DNS 타임아웃/네임서버 오류는 '검증 불가'로 보고 통과시키도록 분기를 나눴다. 이전 구현은 이를 '잘못된 주소'로 처리했다.
- `post()` 하단의 도달 불가능한 중복 저장 코드 6블록: 전부 제거했다.

`docs/error`의 git 추적 여부는 이번 작업에서 바꾸지 않았다.

분석 당시에는 확인하지 못했던 사실 두 가지도 기록해 둔다.

- 통계 모델의 마이그레이션은 `Meta.app_label = "home"` 때문에 `home/migrations/`에 생성된다.
- 저장소에 `migrations/` 디렉터리가 없으면 인자 없는 `makemigrations`는 프로젝트 앱에 아무것도 만들지 않는다. 최초 1회는 앱 이름을 명시해야 한다.
