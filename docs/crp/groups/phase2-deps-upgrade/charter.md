# Charter — phase2-deps-upgrade  (Charter v0.1 / 2026-11-12)

> 상위 기준은 `design-baseline.md`.

## 1. 인벤토리

### 1-1. 하위 단계별 패키지 (현재 → 목표, 2026-11-12 조사 · `poetry` 해석 확인)

| 하위 단계 | 패키지 |
|---|---|
| **2-a 정리·저위험** | Python 조건 `^3.11`→`^3.12`, `testing.yml` 3.11→3.12 · `django-nose` 제거 · `isort` 본 그룹→dev(5.13→9.0) · beautifulsoup4 4.13→4.15 · celery 5.4→5.7 · django-celery-beat 2.7→2.9 · django-celery-results 2.5→2.6 · django-cors-headers 4.7→4.9 · django-braces 1.16→1.17 · django-sendgrid-v5 1.2.4→1.3.1 · psycopg2-binary 2.9.10→2.9.13 · pymysql 1.1→1.2 · email-validator 2.2→2.3 · pytest-django 4.10→4.14 · pytest-factoryboy 2.7→2.8 · coverage 7.6→7.17 · daphne 4.1→4.2 |
| **2-b Django 5.2 LTS** | Django 4.2.19→5.2.x · django-silk 5.3→5.6(Django ≥5.2 필요) · 해석상 함께 올라가야 하는 패키지 |
| **2-c Django 6.0** | Django 5.2→6.0.10(ADR-001) · 해석상 함께 올라가야 하는 패키지 |
| **2-d 서드파티 메이저** | django-allauth 0.58→65.22 · django-recaptcha 3→4.1 · django-redis 5.4→7.0(redis-py 8.1) · sentry-sdk 1.45→2.74 · django-debug-toolbar 4.4→8.0 · django-imagekit 5→6.1 · django-mptt 0.15→0.21 · django-anymail 10→15.2 · django-extensions 3.2→4.1 · django-admin-rangefilter 0.11→0.15 · uvicorn 0.30→0.54 |
| 변경 없음(이미 최신, 오래된 패키지) | django-summernote 0.8.20 · django-user-agents 0.4.0 · django-request-logging 0.7.5 · py3-validate-email · python-gettext · django-decouple — 새 Django에서 런타임 호환은 테스트·runserver로 확인한다 |

### 1-2. 코드 수정 예정 파일

| 파일 | 이유 | 단계 |
|---|---|---|
| `pyproject.toml`, `poetry.lock` | 버전 조건·잠금 | 전체 |
| `.github/workflows/testing.yml` | Python 3.12 (U2) | 2-a |
| `common/mixin/admin/trim_html_tags.py` | 인자 없는 `format_html` 2곳 → `strip_tags` (ADR-004) | 2-b |
| `config/settings/{dev,prod,stage,test}.py`, `portfolio/forms.py`, `users/views/users_forms.py`, `portfolio/tests/test_get_in_touch_captcha.py` | `captcha` → `django_recaptcha` (ADR-005) | 2-d |
| `config/settings/sub_settings/oauth/allauth_default.py`, `config/settings/base.py` | allauth 65의 바뀐 설정 이름(예: `ACCOUNT_EMAIL_REQUIRED`→`ACCOUNT_SIGNUP_FIELDS`) | 2-d |
| 그 밖에 5.2의 `RemovedInDjango60Warning`·서드파티 경고가 가리키는 곳 | 발견 시 ledger 등록 후 수정 범위가 C-3 안이면 수정, 밖이면 멈춤 | 2-b~2-d |

## 2. 계약
### 2-1. 지원 구성
- Python 3.12(로컬 3.12.7), `config.settings.test`(SQLite + Redis) 로 pytest, `config.settings.dev`(PostgreSQL + Redis) 로 runserver.
### 2-2. 위협 모델
- 방어한다: 업그레이드로 인한 기능 회귀, 우리 스키마의 의도치 않은 변경, admin 제목 HTML 미이스케이프(ADR-004).
- 방어하지 않는다: 서버 Python·OS 호환(인프라 범위 밖, R-001).
### 2-3. 불변식
- INV-1: 각 하위 단계 후 전체 pytest가 통과한다(테스트 수는 줄지 않는다).
- INV-2: 각 하위 단계 후 `manage.py check --settings=config.settings.dev`에 ERROR가 없다.
- INV-3: 각 하위 단계 후 우리 앱(users blog board home portfolio custom_middlewares)에 대해 `makemigrations --check --dry-run`이 "No changes".
- INV-4: 각 하위 단계 후 runserver 점검표(§3)가 통과한다.
- INV-5: 2-b 완료 시 `-W error::django.utils.deprecation.RemovedInDjango60Warning`로 pytest가 통과한다.
### 2-4. 비목표
- 새 기능 도입, 새 Django 기능으로의 리팩토링(예: async 뷰), 오래된 패키지 교체(교체가 필요해지면 멈추고 묻는다), psycopg2→psycopg3 전환.

## 3. 인수 기준
- [ ] 2-a~2-d 각각: INV-1~4 확인 후 커밋 1개 이상
- [ ] 2-b 끝: INV-5 통과
- [ ] 최종: `poetry show --outdated --top-level`에 남은 항목은 ADR-001(Django 6.1)처럼 사유가 기록된 것뿐
- [ ] runserver 점검표: `/`·`/portfolio/`·`/blog/blog/` 200 · static 200 · `/wp.php` 404 · admin 로그인 페이지 200 · 로그인 페이지(allauth) 200 · 문의 폼 제출(잘못된 값 거절·정상 값 저장) · 상세 수정 버튼은 작성자만 · 댓글 작성·삭제 · Redis에 `*user_auth*` 키 없음
- [ ] 불가침 제약 C-1~C-6 위반 없음

## 4. 변경 이력
- v0.1 (2026-11-12): 최초 작성.
