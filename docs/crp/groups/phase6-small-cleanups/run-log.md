# Run Log — phase6-small-cleanups

## 작업 계획 (승인됨, 실행됨)
| 순서 | 단계 |
|---|---|
| 1 | 항목별 실패 테스트(N2+, M4, M8, R3, R2, 닉네임, N3) |
| 2 | 수정(영향 큰 순: N2+ → M4 → 닉네임 → M8 → R2 → R3 → 죽은 코드), N3은 테스트가 실패하는 곳만 |
| 3 | fail-on-revert 확인 |
| 4 | 전체 pytest·check·migration, runserver 점검표(태그 수정 왕복·태그 검색 페이지) |
| 5 | 문서·커밋(push 안 함) |

## 라운드 로그

### Round 1 — 2026-11-14 (브랜치 `crp/phase6-small-cleanups`, `fe00ffe` 위)
- **트리거:** 사용자 "d1 a, d2 a, d3 a"
- **red:** 새 테스트 28개 중 17개 실패(수정 폼 태그 `pythondjango` 재현, 공백 태그, 141자 저장, 태그 검색 12개 한 페이지, 닉네임 `IntegrityError`, 옛 file2 남음, `UserVerification` admin 행 9개에 +26 쿼리, `contest.com`·`latest.io` 거부, 가입 `UnboundLocalError`, mac → `oth`). 테스트 쪽 수정 3건(첫 POST 폼이 로그아웃 폼, 검색 URL 이름, 필수 필드 채우기)과 admin 쿼리 수 흔들림(±2) 대응(9행 추가 시 9 미만 증가로 판정)
- **실행 중 발견:** F-010(가입 이메일 검사 500). 같은 함수에서 D1-A를 완성하는 한 줄이라 ADR-005 안에서 처리
- **green:** 28 passed. fail-on-revert 12건 각각 실패 확인
- **기존 테스트 갱신 1건:** `portfolio/tests/test_get_in_touch_form.py::test_test_domains_are_rejected`가 `mytest.co.kr` 거부를 기대(옛 부분 문자열 규칙). D1-A 계약에 맞춰 거부 사례를 `mail.test.co.kr`로 바꾸고, `mytest.co.kr`·`contest.com` 통과 테스트를 추가(지우거나 skip하지 않음)
- **게이트:** pytest **722 passed / 1 skipped**, check exit 0, 이쪽 앱 `makemigrations --check` No changes. dev 스택(PostgreSQL·실제 라우터): 프로젝트 글 수정 화면 그대로 저장 → 302·태그 유지, 141자 태그 → 폼 오류, 태그 검색 12개 → 10+2, 제목·페이지 링크에 검색어. runserver 점검표·5단계 댓글 점검 통과, mac UA 요청 200, 500 0건
- **수렴 판정:** `CONVERGED` — Open Fix 0
- **검사 범위의 한계:** 브라우저에서 직접 누르지 않음. CI 미실행. 이미 합쳐진 태그·mac 통계는 보정 안 함(R-001)
