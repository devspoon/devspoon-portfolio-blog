# Ledger — phase5-request-security (결함 원장)

| ID | Severity | 위반 계약 조항 | 결정 | Status | 근거 | 비고 |
|---|---|---|---|---|---|---|
| F-001 | HIGH | INV-1 | Fix(ADR-001) | Fixed | charter P-1 | 캐시 재생성이 replica에서, TTL 24시간 |
| F-002 | MED | INV-1 | Fix(ADR-001) | Fixed | charter P-2 | 트랜잭션 안 replica 읽기로 `group` 중복 가능 |
| F-003 | MED | INV-3 | Fix(ADR-003) | Fixed | charter P-3·P-4·P-5 | 댓글 생성 검증(M5) |
| F-004 | MED | INV-3 | Fix(ADR-004) | Fixed | charter P-6 | 댓글 수정 검증(형제 버그) |
| F-005 | MED | INV-1(계획 밖, 실행 중 발견) | **사용자 결정 대기** | Open | `users/models.py:485` `on_save_user` | 사용자를 저장할 때마다(로그인의 `last_login` 저장 포함) 프로필이 있는지 replica에서 확인하고, 없으면 만든다. replica가 늦으면 이미 있는 프로필을 또 만들려다 `nickname` 중복 `IntegrityError`(500). POST 로그인은 이번 미들웨어로 primary에서 읽지만, GET으로 끝나는 흐름(소셜 로그인 콜백 등)은 그대로. 테스트 `test_reply_create_reads_the_primary_inside_the_request`가 발견(로그인을 라우터 켜기 전으로 옮겨 우회) |
| F-006 | LOW | INV-3 | Fix(ADR-002, 형제 버그) | Fixed | 블로그 댓글 수정 뷰 5개의 `get()` | `redirect("…_reply_update", reply_pk)`가 인자 2개짜리 URL을 1개로 만들어 GET이 `NoReverseMatch` 500이었다. mixin으로 모으며 게시판 3개처럼 `get()`이 없어져 405 |
