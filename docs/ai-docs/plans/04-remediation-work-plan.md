# Remediation Work Plan

갱신일: 2026-08-10

| Phase | 내용 | 상태 |
| --- | --- | --- |
| 0 | nginx 1차 차단 | 미적용 (운영 작업) |
| 1 | Django 2차 차단 미들웨어 | 완료 |
| 2 | 통계 중복 정리 및 모델 개선 | 코드 완료, 운영 DB 실행 대기 |
| 3 | 문의 폼 검증 개선 | 완료 |
| 4 | 메일 발송 실패 처리 | 코드 완료, SendGrid 계정 점검 대기 |
| 5 | 관측 및 회귀 방지 | 완료 |

구현 상세와 배포 절차는 [../reports/06-implementation-report.md](../reports/06-implementation-report.md)에 있다.

## Phase 0: 운영 차단

상태: **미적용 (운영 작업)**

담당 후보: 운영자 또는 배포 담당 에이전트

1. nginx 설정에 [../security/02-nginx-php-scan-blocking.md](../security/02-nginx-php-scan-blocking.md)의 PHP/WordPress 차단 location을 추가한다.
2. default server로 미등록 Host 접근을 차단한다.
3. `nginx -t` 후 reload한다.
4. curl과 access log로 `.php` 요청이 gunicorn까지 도달하지 않는지 확인한다.

완료 기준:

- gunicorn access log에서 신규 `.php` 요청이 사라진다.
- Sentry의 PHP 스캔 관련 이벤트가 감소한다.

## Phase 1: Django 2차 차단 미들웨어

상태: **완료**

담당 후보: Codex

1. `custom_middlewares/middlewares/access_guard.py`를 추가한다.
2. `BlockSuspiciousPathMiddleware`를 구현한다.
3. `config/settings/base.py`의 `MIDDLEWARE`에서 통계 미들웨어보다 앞에 삽입한다.
4. 단위 테스트를 추가한다.

테스트 후보:

- `GET /wp.php`
- `GET /site/phpinfo.php`
- `GET /bbs/board.php`
- `GET /portfolio/`

완료 기준:

- 차단 URL은 조기 404 또는 설정 status를 반환한다.
- 차단 URL 요청은 통계 row를 변경하지 않는다.
- 정상 URL의 기존 테스트가 통과한다.

## Phase 2: 통계 테이블 중복 정리 및 모델 개선

상태: **코드 완료. 운영 DB에서 `dedupe_connection_stats` 실행이 남아 있다.**

담당 후보: Claude 또는 Codex

1. 운영 DB에서 중복 현황을 조회한다.

```sql
SELECT DATE(created_at) AS stat_date, COUNT(*)
FROM connection_method_stats
GROUP BY DATE(created_at)
HAVING COUNT(*) > 1;

SELECT DATE(created_at) AS stat_date, COUNT(*)
FROM connection_hardware_stats
GROUP BY DATE(created_at)
HAVING COUNT(*) > 1;
```

2. 날짜별 중복 row의 카운트를 합산하고 대표 row 1개만 남기는 data migration 또는 운영 스크립트를 만든다.
3. 모델에 명시적 일자 필드를 추가한다.

```python
stat_date = models.DateField(unique=True, db_index=True)
```

4. 통계 미들웨어 조회키를 `created_at__date`에서 `stat_date`로 변경한다.
5. 동시 생성 경합은 유니크 제약과 `IntegrityError` retry로 처리한다.

주의:

- 현재 모델은 `custom_middlewares/models.py`에 있으나 `Meta.app_label = "home"`으로 DB app label을 `home`으로 잡는다.
- 마이그레이션 파일 위치와 앱 라벨을 실제 Django가 어떻게 인식하는지 `makemigrations --dry-run`으로 확인해야 한다.
- 운영 데이터 백업 후 적용한다.

완료 기준:

- 같은 날짜 row가 1개만 존재한다.
- 동시 요청 테스트에서 중복 row가 생기지 않는다.
- 기존 admin 통계 화면이 정상 동작한다.

## Phase 3: 문의 폼 검증 개선

상태: **완료**

담당 후보: Codex

1. `portfolio/forms.py`를 추가하거나 기존 패턴에 맞는 위치에 `GetInTouchForm`을 만든다.
2. 입력 필드 정책을 정의한다.

| 필드 | 정책 |
| --- | --- |
| name | 필수, trim, 최대 300자 |
| emailfrom | 필수, EmailField, DNS 검증은 timeout/fallback 고려 |
| number | 선택, 최대 16자, 값이 있으면 phone validator 적용 |
| subject | 필수, trim, 최대 300자 |
| message | 필수, trim, 최대 길이 정책 필요 |

3. `GetInTouchView.post()`를 form 기반으로 단순화한다.
4. `check_email_validation_with_dns()`의 `is_valid` 초기화 문제를 수정한다.
5. 도달 불가능한 중복 코드를 제거한다.
6. 스팸성 요청에 대해 rate limit 또는 captcha 적용을 검토한다. 이미 운영 `INSTALLED_APPS`에 `captcha`가 추가되어 있으므로 활용 가능성을 확인한다.
   → `CONTACT_FORM_CAPTCHA` 설정으로 reCAPTCHA를 적용했다. prod/stage에서만 켠다. rate limit은 적용하지 않았다.

완료 기준:

- 16자 초과 전화번호 입력은 DB insert 전에 form error로 종료된다.
- Sentry의 `DataError value too long for type character varying(16)`가 재발하지 않는다.
- 정상 문의는 저장과 사용자 메시지가 정상 동작한다.

## Phase 4: 메일 발송 실패 처리

상태: **코드 완료. 운영 SendGrid 계정 점검이 남아 있다.**

담당 후보: Claude 또는 Codex

1. 운영 SendGrid 상태를 확인한다.
   - API key 유효성
   - sender/domain 인증
   - 크레딧/과금 한도
   - sandbox mode 여부
2. `utils/email/async_send_email.py`의 스레드 기반 발송 정책을 재검토한다.
3. Celery task 기반으로 전환하거나, 최소한 발송 결과를 기록하는 wrapper를 만든다.
4. `GetInTouchLog.state`의 의미를 명확히 한다.
   - 후보 A: 문의 접수 여부
   - 후보 B: 메일 발송 성공 여부
   - 후보 C: `status` enum으로 `received`, `queued`, `sent`, `failed`
5. Sentry logging에서 recipient PII를 마스킹한다.

완료 기준:

- 메일 서비스 장애가 사용자 성공 메시지와 혼동되지 않는다.
- 발송 실패가 운영자가 볼 수 있는 상태로 남는다.
- Sentry에 민감정보가 원문으로 남지 않는다.

## Phase 5: 관측 및 회귀 방지

상태: **완료**

1. Sentry ignore/filter 정책을 정리한다.
2. PHP scan 차단량을 nginx access log 또는 별도 metric으로 집계할지 결정한다.
3. 통계 미들웨어 테스트를 CI에 포함한다.
4. 문의 폼 악성 입력 테스트를 추가한다.

완료 기준:

- 실제 장애와 스캔 노이즈가 분리된다.
- 같은 유형의 Sentry 이벤트가 재발하면 담당자가 원인을 바로 추적할 수 있다.
