# Ledger — phase2-deps-upgrade (결함 원장)

| ID | Severity | 위반 계약 조항 | 결정 | Status | 근거 | 비고 |
|---|---|---|---|---|---|---|
| F-001 | HIGH | INV-5, 위협 모델 | Fix(ADR-004) | Fixed | `common/mixin/admin/trim_html_tags.py:8,25` | 인자 없는 `format_html` — Django 5.x에서 경고(`RemovedInDjango60Warning`), 6.0에서 제거. 현재는 제목 HTML을 이스케이프 없이 출력(admin 저장 XSS 여지) |
| F-002 | HIGH | INV-2(4.x에서 import 실패) | Fix(ADR-005) | Fixed | 설정 4개, `portfolio/forms.py`, `users/views/users_forms.py`, `portfolio/tests/test_get_in_touch_captcha.py` | django-recaptcha 4의 import 경로 변경 |
| F-003 | MED | INV-2 | Fix | Fixed | `config/settings/sub_settings/oauth/allauth_default.py:74` 외 | allauth 65에서 이름이 바뀐 설정. 경고로 확정된 것은 `ACCOUNT_EMAIL_REQUIRED` 하나 → `ACCOUNT_SIGNUP_FIELDS = ["email", "username*", "password1*", "password2*"]`(같은 뜻). 소셜 로그인 의존성이 extras로 바뀐 것도 함께 반영 |
| F-004 | LOW | (계약 밖 — 결정 대기) | 미정 | Open | `requirements/dev.txt`, `README.md:148` | 실행 중 발견. README는 `pip install -r requirements/dev.txt`를 안내하지만 이 파일은 이미 lock과 다르다(Django 4.2.11 등). CI는 poetry를 쓴다(`testing.yml:57-59`). 계획에 없던 파일이라 수정하지 않고 결정 대기 |
| F-005 | LOW | INV-5(일부) | 미정 — 결정 대기 | Open | `blog/views/blog/blog_forms.py:13` 외 ModelForm·admin 폼, 모델 URLField 34개(`blog/models/blog.py`, `portfolio/models.py`, `users/models.py`, `home/models/default.py`) | 실행 중 발견. 5.2에서 6.0 폐지 예정 경고는 이것 하나뿐: `forms.URLField` 기본 scheme이 6.0에서 http→https로 바뀐다는 경고. 없애려면 scheme 없는 입력을 http로 볼지 https로 볼지 정해야 한다(사용자에게 보이는 동작, C-3). 5.2에서는 경고일 뿐 동작 영향 없음. 수정하지 않고 결정 대기 |
| F-006 | LOW | (계약 밖 — 결정 대기) | 미정 | Open | `config/settings/prod.py:186`, `config/settings/stage.py`의 `sentry_sdk.init(..., send_default_pii=True)` | 실행 중 발견. sentry-sdk 2.74에서 `send_default_pii`가 deprecated(대체: `data_collection`). 지금은 경고만 나고 동작은 같다. 이 옵션은 Sentry로 보내는 개인정보 범위를 정하므로 바꾸는 것은 개인정보 수집 결정이라 수정하지 않고 결정 대기 |
