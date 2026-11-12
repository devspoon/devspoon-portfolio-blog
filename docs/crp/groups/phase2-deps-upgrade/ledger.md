# Ledger — phase2-deps-upgrade (결함 원장)

| ID | Severity | 위반 계약 조항 | 결정 | Status | 근거 | 비고 |
|---|---|---|---|---|---|---|
| F-001 | HIGH | INV-1(6.0에서 오류) | Fix(ADR-004) | Open | `common/mixin/admin/trim_html_tags.py:8,25` | 인자 없는 `format_html` — Django 6.0에서 제거. 현재는 제목 HTML을 이스케이프 없이 출력(admin 저장 XSS 여지) |
| F-002 | HIGH | INV-2(4.x에서 import 실패) | Fix(ADR-005) | Open | 설정 4개, `portfolio/forms.py`, `users/views/users_forms.py`, `portfolio/tests/test_get_in_touch_captcha.py` | django-recaptcha 4의 import 경로 변경 |
| F-003 | MED | INV-2 | Fix | Open | `config/settings/sub_settings/oauth/allauth_default.py:74` 외 | allauth 65에서 이름이 바뀐 설정. 정확한 목록은 업그레이드 후 allauth 경고로 확정 |
