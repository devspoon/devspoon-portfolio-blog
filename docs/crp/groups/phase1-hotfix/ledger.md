# Ledger — phase1-hotfix (결함 원장)

| ID | Severity | 위반 계약 조항 | 결정 | Status | 근거 | 비고 |
|---|---|---|---|---|---|---|
| F-001 | CRIT | INV-1, INV-3 | Fix | Open | `blog/views/blog/blog_blog.py:117` 외 상세 뷰 8개 | C1. `user_auth=request.user`(User 객체)를 글 단위로 캐시. 첫 방문자 정보가 모두에게 공유되고 비밀번호 해시가 Redis에 들어감. `AnonymousUser`가 참이라 버튼이 항상 보임 |
| F-002 | CRIT | INV-2, INV-3 | Fix | Open | `blog/views/blog/blog_blog.py:110-115` 외 블로그 상세 5개 | C1. `like_state`를 글 단위로 캐시 |
| F-003 | HIGH | INV-1 | Fix | Open | `blog/views/blog/blog_reply.py:74` 외 댓글 목록 8개 | C1(댓글). 댓글별 `user_auth`가 첫 요청자 기준으로 캐시됨 |
| F-004 | CRIT | INV-4 | Fix | Open | `blog/models/blog_reply.py:107` | C2. `post_delete`에서 지워진 행을 다시 조회해 `DoesNotExist`가 나고 삭제 전체가 롤백됨 |
| F-005 | CRIT | INV-4 | Fix | Open | `board/models/board_reply.py:67` | C2 형제 버그. board 댓글 3개 모델에서 같은 결함 |
| F-006 | MED | INV-5 | Fix | Open | `blog/views/blog/blog_reply.py:69`, `board/views/notice/notice_reply.py:71` 외 | N1. `context.post.pk`·`context.board.pk`가 댓글마다 쿼리를 냄 |
| F-007 | MED | 인수기준 M2 | Fix | Open | `blog/views/books/books_blog.py:21`, `blog/views/online_study/online_study_blog.py:20` | M2. 쓰지 않는 `from isort import file`. 운영에서 dev 의존성을 빼면 URLconf 로딩 실패 |
