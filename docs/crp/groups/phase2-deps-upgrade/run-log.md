# Run Log — phase2-deps-upgrade (라운드 로그 + 수렴 판정)

## 라운드 기록

### Round 0 — 2026-11-12 (base SHA: `584a955`, 브랜치 `crp/phase2-deps-upgrade`)
- **트리거:** 사용자 요청("모든 패키지 최신화 허용", U1~U3 권장안)
- **조사:** `poetry show --outdated --top-level` 28개. 임시 사본(`pyproject.toml`·`poetry.lock`)에서 해석 시험:
  - Python `^3.11`에서는 Django 6.x 해석 불가(6.x는 Python ≥3.12)
  - Django `^6.1`은 `django-celery-beat` 2.9.0(`Django <6.1`) 때문에 해석 불가
  - Django `^6.0` + 주요 메이저 전부 → 해석 성공(Django 6.0.10, allauth 65.22.0, recaptcha 4.1.0, django-redis 7.0.0, sentry-sdk 2.74.0, debug-toolbar 8.0.0, silk 5.6.0, celery 5.7.0, redis 8.1.0)
  - Django 5.0·6.0 릴리스 노트 대조: `DEFAULT_AUTO_FIELD`는 이미 BigAutoField, `USE_TZ=True`, 로그아웃은 자체 View라 해당 없음. 인자 없는 `format_html` 2곳 발견(F-001)
- **수렴 판정:** `NOT CONVERGED`(설계 단계)

### Round 0.1 — 2026-11-12 (설계 수정, REQ-002)
- **트리거:** 사용자 요청("django는 5.2 LTS로 정의")
- **재조사:** 임시 사본에서 `Django = "~5.2"` + 서드파티 최신 메이저로 `poetry lock` → 해석 성공. Django 5.2.19, allauth 65.22.0, recaptcha 4.1.0, django-redis 7.0.0, sentry-sdk 2.74.0, debug-toolbar 8.0.0, silk 5.6.0, celery-beat 2.9.0, celery 5.7.0, imagekit 6.1.1, mptt 0.21.1, anymail 15.2, extensions 4.1, redis 8.1.0 — Django 6.0 목표 때와 서드파티 버전이 같다
- **변경:** ADR-007(5.2 LTS)이 ADR-001 대체, ADR-008(4.2→5.2 직행)이 ADR-002 대체. Django 6.0 단계 삭제, 서드파티 메이저 단계를 2-c로
- **수렴 판정:** `NOT CONVERGED`(설계 단계)

### Round 1 — 2026-11-12 (base SHA: `f095ff8`, 설계 승인 후 실행)
- **기준선:** 우리 앱 `makemigrations --check` No changes, pytest 210 passed / 1 skipped. runserver 점검표에서 `/users/login/` 500 → 원인은 코드가 아니라 로컬 DB에 `SocialApp`(google·kakao·naver) 행이 없던 것(템플릿의 `provider_login_url`). 로컬 dev DB에만 더미 SocialApp 3개를 등록한 뒤 점검표 전부 통과
- **2-a 정리·저위험:** Python `^3.12`, `testing.yml` 3.12, `django-nose`·`nose` 제거, `isort` dev 그룹(9.0.2), 같은 메이저 업데이트(celery 5.7, beat 2.9, results 2.6, cors 4.9, braces 1.17, sendgrid-v5 1.3.1, psycopg2 2.9.13, pymysql 1.2.4, bs4 4.15, email-validator 2.3, daphne 4.2.3, pytest-django 4.14, factoryboy 2.8.1, coverage 7.17.2). `poetry lock --no-update`로 바뀐 조건만 재해석. celery-results migration 3개 적용
  - 검증: check exit 0, 우리 앱 No changes, pytest 210 passed / 1 skipped, runserver 점검표 통과
  - 참고: 설치 직후 첫 `check`가 psycopg2 import 오류로 1회 실패했으나(같은 시점에 `migrate` 동시 실행) 재실행 2회 모두 통과, 재현 안 됨
- **신규 finding:** F-004(LOW, `requirements/dev.txt`가 lock과 불일치) — 계획 밖, 결정 대기
- **2-b Django 5.2 LTS:**
  - ① 4.2에서 `RemovedInDjango50Warning`·`RemovedInDjango51Warning`을 오류로: pytest 210 passed, `check` 통과 — 해당 사용처 0건
  - ② `Django = "~5.2"`(5.2.19), django-silk 5.6.0. 함께 빠진 것: autopep8·pycodestyle(silk 5.3의 하위 의존성). 우리 앱 No changes, 새 migration 없음
  - ③ `RemovedInDjango60Warning`을 오류로: `forms.URLField` 기본 scheme 경고 1종만 발생(ModelForm·admin 폼). scheme 결정이 필요해 수정하지 않고 F-005로 기록
  - F-001 수정: `strip_tags`로 교체, 테스트 2개(수정 전 실패 확인). admin 블로그 글 목록·수정 화면 200, 부제목이 `Bold title`로 태그 제거됨
  - 검증: check exit 0, 우리 앱 No changes, pytest 212 passed / 1 skipped, runserver 점검표 통과
- **2-c ① django-redis 5.4 → 7.0.0, redis-py 5.2.1 → 8.1.0:** 코드 변경 없음. check exit 0, 우리 앱 No changes, pytest 212 passed / 1 skipped, runserver 점검표 통과. Redis에서 상세 캐시 키(`pre_board`·`next_board`·`get_queryset`) TTL 약 24시간, 세션 키 저장 확인
- **2-c ② django-recaptcha 3.0 → 4.1.0 (F-002):** 옛 `captcha` 패키지는 `--sync`로 제거. `INSTALLED_APPS` 4곳 `captcha`→`django_recaptcha`, import 3곳(`portfolio/forms.py`, `users/views/users_forms.py` 2줄), 테스트 mock 대상 `django_recaptcha.fields.client.submit`, 주석의 check ID `django_recaptcha.recaptcha_test_key_error`. check exit 0, 우리 앱 No changes, pytest 212 passed / 1 skipped(캡차 테스트 8개 포함), runserver 점검표 통과, `/users/register/` 200·`g-recaptcha` 위젯 표시
- **2-c ③ django-allauth 0.58 → 65.22.0 (F-003):** 처음 올리자 소셜 로그인 의존성(pyjwt·oauthlib 등)이 빠짐 → 65부터 extras로 분리된 것이라 `extras = ["socialaccount"]`로 지정(oauthlib 4.0.1·pyjwt 2.15.1). allauth 경고 `ACCOUNT_EMAIL_REQUIRED is deprecated` → `ACCOUNT_SIGNUP_FIELDS`로 같은 뜻 교체. 커스텀 어댑터(`pre_social_login`·`populate_user`)는 수정 불필요. `account` migration 0006~0009 dev DB 적용(R-005). check exit 0(allauth 경고 0), 우리 앱 No changes, pytest 212 passed / 1 skipped, runserver 점검표 통과, `/oauth/{google,kakao,naver}/login/` 302 → 각 provider 인증 URL, `/users/register/` 200

## 작업 계획 (승인 후 실행 — 순서 고정)

각 하위 단계는 같은 절차를 따른다.
1. `pyproject.toml` 조건 변경 → `poetry lock` → `poetry install --with dev,test`
2. `manage.py check`(INV-2), 전체 pytest(INV-1), 우리 앱 `makemigrations --check --dry-run`(INV-3)
3. 서드파티 migration이 있으면 dev DB에 `migrate`
4. runserver 점검표(INV-4, charter §3)
5. 실패나 경고가 나오면 ledger에 기록. 수정이 C-3 범위 안이면 수정하고, 밖이면 멈추고 묻는다
6. 하위 단계별 커밋

| 순서 | 하위 단계 | 특이 사항 |
|---|---|---|
| 0 | 기준선 | 업그레이드 전 우리 앱 migration(이미 생성됨, git 무시)과 `makemigrations --check` 상태 확인 |
| 1 | 2-a 정리·저위험 | `testing.yml` Python 3.12 · `django-nose` 제거 · `isort` dev 그룹 |
| 2 | 2-b Django 5.2 LTS | ① 4.2에서 `RemovedInDjango50/51Warning`을 오류로 바꿔 pytest, 걸리는 곳 수정 ② `Django = "~5.2"`로 올림(5.2.19) ③ `RemovedInDjango60Warning`을 오류로 바꿔 pytest(INV-5). F-001 수정 |
| 3 | 2-c 서드파티 메이저 | 묶음: ① django-redis 7(+redis-py) ② recaptcha 4(F-002) ③ allauth 65(F-003) ④ sentry 2·debug-toolbar 8·extensions 4 ⑤ imagekit 6·mptt 0.21·anymail 15·rangefilter 0.15·uvicorn. 묶음마다 위 절차로 검증 |
| 4 | 마무리 | `poetry show --outdated --top-level` 결과 기록(Django는 5.2 LTS 고정이 사유), 수렴 판정 |

## 심각도 추세
| Round | CRIT | HIGH | MED | LOW | 신규 Fix | 판정 |
|---|---|---|---|---|---|---|
| 0 | 0 | 2 | 1 | 0 | 3 | NOT CONVERGED(설계) |
