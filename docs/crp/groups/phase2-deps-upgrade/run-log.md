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
- **2-c ④ sentry-sdk 1.45 → 2.74.0, django-debug-toolbar 4.4 → 8.0.0, django-extensions 3.2 → 4.1:** 이 묶음부터 `stage` 그룹도 설치해 sentry를 확인. sentry는 prod와 같은 옵션(`DjangoIntegration`, `traces_sample_rate`, `send_default_pii`, `before_send`)으로 DSN 없이 초기화 성공, `send_default_pii` deprecated 경고 → F-006. debug-toolbar 8은 `LoggingPanel`을 스스로 빼고 "설정에서 제거하라"는 경고를 냄 → dev 설정 패널 목록에서 제거(동작 변화 없음). check exit 0, 우리 앱 No changes, pytest 212 passed / 1 skipped, runserver 점검표 통과, 툴바 표시, `show_urls` 동작
- **2-c ⑤ django-imagekit 5.0 → 6.1.1, django-mptt 0.15 → 0.21.1(+django-js-asset 5.0), django-anymail 10.3 → 15.2, django-admin-rangefilter 0.11 → 0.15.0, uvicorn 0.30 → 0.54.0:** 코드 변경 없음(rangefilter는 이미 `rangefilter.filters` 경로 사용). check exit 0, 우리 앱 No changes(mptt 모델 포함), pytest 212 passed / 1 skipped, runserver 점검표 통과. admin 메뉴(mptt 드래그 admin)·날짜 범위 필터 목록·사용자 목록 200. 댓글 목록의 작성자 썸네일 URL 요청 시 imagekit이 `media/CACHE/...`에 생성하고 200 `image/jpeg`로 서빙
- **마무리:** `poetry show --outdated --top-level` → Django 5.2.19(최신 6.1.3)만 남음, 사유 ADR-007. 하위 의존성 48개 outdated(보안 관련 cryptography·pillow·urllib3·requests·certifi 포함) → F-007
- **Fix 결과:** F-001·F-002·F-003 Fixed(각각 수정 전 실패 확인 또는 경고로 확정). 이번 라운드 테스트 2개 추가(212개)
- **결정 대기(계약 밖·사용자에게 보이는 동작·개인정보):** F-004(`requirements/dev.txt`), F-005(URLField 기본 scheme, INV-5), F-006(sentry `send_default_pii`), F-007(하위 의존성)
- **GATE 통과:** 0 ■ 1 ■ 2 ■ 3 □(INV-5 미완, F-005) 4 ■ 5 □
- **수렴 판정:** `NOT CONVERGED` — Open Fix 0이지만 불변식 INV-5가 F-005 결정을 기다린다
- **검사 범위의 한계:** CI 미실행(push 안 함). 운영 설정(prod·stage)으로는 runserver를 띄우지 않았다(인프라 범위 밖). 소셜 로그인은 provider redirect까지만 확인(실제 인증 콜백은 더미 키라 불가, R-004)

### Round 2 — 2026-11-12 (base SHA: `fb33df7`, REQ-003 결정 반영)
- **트리거:** 사용자 "권장대로 승인한다"(F-004~F-007)
- **F-007:** `poetry update` — 하위 의존성 갱신 51·추가 6(markupsafe, werkzeug, pygments, msgpack, ujson, cbor2)·제거 4(pyasn1, pyasn1-modules, setuptools, starkbank-ecdsa). 메이저 변경: cryptography 44→50, pillow 11→13, pytest 8→9, soupsieve 2→4, zope-interface 7→8, twisted 24→26 등. `--with dev,test,stage --sync`로 설치
  - 검증: check exit 0, 우리 앱 No changes, pytest 212 passed / 1 skipped, runserver 점검표 통과. 추가로 `/oauth/{google,kakao,naver}/login/` 302 → provider, imagekit 썸네일 50×50 JPEG 생성(pillow 13.0.0), sentry 2.74 prod 옵션 초기화 성공
  - 남은 outdated: Django 5.2.19(ADR-007), cron-descriptor 1.4.5·filelock 3.32.7·python-dateutil 2.9.0.post0(상위 패키지의 버전 상한 때문에 해석이 허용하지 않음)
- **F-005:** 코드 변경 없음. `-W error::...RemovedInDjango60Warning -W "ignore:The default scheme will be changed:...RemovedInDjango60Warning"`로 pytest 212 passed / 1 skipped(필터 없이는 실패하던 경고라 예외가 그 1종에만 걸림)
- **F-004:** `poetry export --with dev --without-hashes -f requirements.txt -o requirements/dev.txt`(97줄). `pip install --dry-run -r requirements/dev.txt` exit 0
- **F-006:** 변경 없음, R-007
- **참고(범위 밖, 기록만):** `fabfile.py:24`가 저장소에 없는 `requirements/prod.txt`를 쓴다. 인프라 파일이라 건드리지 않음
- **GATE 통과:** 0 ■ 1 ■ 2 ■ 3 ■ 4 ■ 5 ■
- **수렴 판정:** `CONVERGED` — Open Fix 0, INV-1~5 통과, 인수 기준 충족, 요구사항 회귀 0
- **검사 범위의 한계:** CI 미실행(push 안 함). prod·stage 설정으로 runserver를 띄우지 않음. 소셜 로그인은 provider redirect까지만(R-004)

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
| 1 | 0 | 0 | 1 | 3 | 3 Fixed(F-001~003), 결정 대기 4(F-004~007) | NOT CONVERGED(INV-5) |
| 2 | 0 | 0 | 0 | 0 | 2 Fixed(F-004·007), 2 Accepted(F-005·006) | CONVERGED |
