# 트랙 B — Django 4.2 → 5.2 LTS 업그레이드 계획 (Proposed, 2026-11-17)

> 상태: **승인 대기**. 조사만 했고 코드·의존성은 바꾸지 않았다. 근거는 PyPI(`https://pypi.org/project/<pkg>/<ver>/`)와
> Django 릴리스 노트(https://docs.djangoproject.com/en/5.2/releases/5.2/). 버전은 `poetry.lock` 기준
> (`requirements/dev.txt`는 lock과 어긋나 있음 — 예: Django 4.2.11 vs lock 4.2.19).

## 1. 막히는 것
| # | 항목 | 현재 | 해결 |
|---|---|---|---|
| B-1 | `django-celery-beat` 2.7.0이 `Django<5.2` 요구 | 2.7.0 | 2.8.0 이상 |
| B-2 | `pyproject.toml:10` `Django = "^4.2.7"`(= `<5.0`) | — | 제약 변경 |
| B-3 | `django-recaptcha` 3.0.0은 Django 4.0까지 표기 | 3.0.0 | 4.1.0(모듈 이름 `captcha` → `django_recaptcha`) |
| ~~B-4~~ | 운영 PostgreSQL ≥ 14 필요 | **17.5 (2026-11-17 읽기 전용 확인)** | 해당 없음 |

Python: 선언 3.11(pyproject·CI), 로컬 3.12 — Django 5.2(3.10~3.14) 충족. psycopg2-binary 2.9.10 — 5.2 요건(2.8.4+) 충족.

## 2. 패키지 (현재 → 4.2·5.2 둘 다 지원하는 최소 버전)
| 패키지 | 현재 | 목표 | 주의 |
|---|---|---|---|
| Django | 4.2.19 | 4.2.30 → 5.2.x | |
| django-allauth | 0.58.2 | 65.7+ | `[socialaccount]` extra 필요(0.62+), 이메일 소문자 저장 데이터 마이그레이션(0.63+), `ACCOUNT_EMAIL_REQUIRED` → `ACCOUNT_SIGNUP_FIELDS`(65.5+, 하위 호환) |
| django-redis | 5.4.0 | 6.0.0 | |
| django-recaptcha | 3.0.0 | 4.1.0 | import·INSTALLED_APPS 이름 변경 |
| django-mptt | 0.15.0 | 0.17.0 | `MainMenu` 인덱스 변화 가능(추정) |
| django-anymail | 10.3 | 13.0 | INSTALLED_APPS에만 있음 |
| django-celery-beat / -results | 2.7.0 / 2.5.1 | 2.8.0 / 2.6.0 | |
| django-timezone-field(간접) | 7.1 | 7.2 | |
| django-debug-toolbar / silk / extensions (dev) | 4.4.6 / 5.3.2 / 3.2.3 | 5.1 / 5.4 / 4.0 | |
| pytest-django | 4.10.0 | 4.11.0 | |
| sentry-sdk(stage) | 1.45.1 | 2.x(추정) | 5.2 명시 지원 미확인 |
| summernote 0.8.20.0, imagekit, rangefilter, user-agents, request-logging, sendgrid-v5, braces | 그대로 | — | 분류 정보 없음. 소스 검색으로 제거된 API 사용 없음(추정) — 테스트로 확인 |

## 3. 코드 수정
1. `pyproject.toml` 제약: Django(:10), mptt(:15), allauth(:21, extra), recaptcha(:22), celery-beat(:42, :57)
2. recaptcha 이름 변경: `users/views/users_forms.py:3-5`, INSTALLED_APPS `dev.py:82`·`prod.py:100`·`stage.py:97`·`test.py:90`
3. `common/mixin/admin/trim_html_tags.py:8,25` 인자 없는 `format_html()`(5.0 deprecated, 6.0 제거) — 제목을 HTML로 그대로 표시하므로
   대체 시 이스케이프 유지(`mark_safe` 금지)
4. URLField `assume_scheme` 경고(`RemovedInDjango60Warning`): blog·home·portfolio·users 모델의 URL 필드 — 폼에 `assume_scheme="https"` 지정
5. `pytest.ini:4`의 `-W ignore::DeprecationWarning`을 경고 정리 단계에서만 끄고 실행
6. 죽은 파일 `config/settings/sub_settings/cloud/aws.py`(STATICFILES_STORAGE·DEFAULT_FILE_STORAGE, 5.1 제거 + 평문 키 R-014) — 삭제 후보(사용자 결정)

## 4. 단계 (각 단계 = 커밋 1개 + 전체 테스트, 단계마다 STOP 없이 진행하되 실패 시 멈춤)
1. Django 4.2.30 패치
2. 4.2 상태에서 §2 패키지 올리기 + §3-2(recaptcha) + allauth 설정 (`makemigrations --check`, 로그인·소셜 로그인 흐름 테스트)
3. 경고 정리: `-W error::DeprecationWarning`으로 테스트, §3-3·§3-4
4. Django 5.2.x + `makemigrations --check` + 전체 테스트 + 스크린샷·상호작용 시나리오(댓글·좋아요·로그인)
5. 운영 배포 전: 운영 DB 백업(`pg_dump`), allauth 이메일 소문자 마이그레이션 영향(중복 이메일 여부) 읽기 전용 확인

## 5. 확인 못 한 것 / 위험
- 운영 마이그레이션 상태: `migrations/`가 git 제외, 환경마다 `makemigrations` — allauth·mptt 새 마이그레이션이 운영에서 정상 생성되는지 배포 리허설 필요
- PgBouncer pool 모드: transaction 모드면 `DISABLE_SERVER_SIDE_CURSORS=True` 필요(4.2부터 요구, 현재 설정 없음)
- `prod.py:64` ENGINE 기본값이 MySQL(.env가 PostgreSQL로 덮어씀) — 기본값 정리 여부
- summernote(2021 이후 배포 없음) 등 분류 없는 패키지의 실제 동작은 테스트로만 확인 가능
