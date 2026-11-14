# Ledger — phase6-small-cleanups (결함 원장)

| ID | Severity | 항목 | 결정 | Status | 근거 |
|---|---|---|---|---|---|
| F-001 | HIGH | N2+ 수정 폼 태그 합쳐짐 | Fix(ADR-001) | Fixed | `blog/views/*/*_forms.py` 4개 `"".join` |
| F-002 | MED | N2 `tag_save` 공백·빈 값·140자 | Fix(ADR-001) | Fixed | `blog/models/blog.py:122` |
| F-003 | MED | M4 태그 검색 페이지 나눔·제목 | Fix(ADR-002) | Fixed | `home/views/service/search.py` |
| F-004 | MED | 닉네임 겹침 500(5단계 R-005) | Fix(ADR-006) | Fixed | `users/models.py` `_ensure_profile` |
| F-005 | LOW | M8 옛 파일 남음 | Fix(ADR-003) | Fixed | `blog/models/blog.py:331`, `users/models.py:537` |
| F-006 | LOW | R2 정상 도메인 거부 | Fix(ADR-005, D1) | Fixed | `users/views/users_forms.py:84`, `portfolio/forms.py:90` |
| F-007 | LOW | R3 mac 통계 0 | Fix(ADR-004) | Fixed | `custom_middlewares/middlewares/statistics.py:102` |
| F-008 | LOW | N3 admin 쿼리 | Fix(ADR-007) | Fixed | 테스트 6개 목록 중 `UserVerificationAdmin`만 행 9개에 쿼리 26개 증가(`user`가 NULL 허용 FK라 자동 select_related에서 빠짐) → `list_select_related = ("user",)` |
| F-009 | LOW | 죽은 `__table_name__` | Fix(ADR-008) | Fixed | `blog/models/blog.py:119` |
| F-010 | MED | R2 형제(ADR-005 완성에 필요) | Fix | Fixed | `users/views/users_forms.py` `check_email_validation_with_dns` | 검증 전에 예외(도메인 `test`, DNS 오류)가 나면 정의되지 않은 `is_valid`를 반환해 가입이 `UnboundLocalError` 500. `is_valid = False` 초기값 한 줄. D1-A(정확히 test면 폼 오류로 거부)가 동작하려면 필요해 같은 ADR 안에서 처리하고 보고에 밝힘 |
