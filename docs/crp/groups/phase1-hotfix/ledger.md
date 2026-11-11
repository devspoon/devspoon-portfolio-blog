# Ledger — phase1-hotfix (결함 원장)

| ID | Severity | 위반 계약 조항 | 결정 | Status | 근거 | 비고 |
|---|---|---|---|---|---|---|
| F-001 | CRIT | INV-1, INV-3 | Fix | Fixed | `blog/views/blog/blog_blog.py:117` 외 상세 뷰 8개 | C1. `user_auth=request.user`(User 객체)를 글 단위로 캐시. 첫 방문자 정보가 모두에게 공유되고 비밀번호 해시가 Redis에 들어감. `AnonymousUser`가 참이라 버튼이 항상 보임 |
| F-002 | CRIT | INV-2, INV-3 | Fix | Fixed | `blog/views/blog/blog_blog.py:110-115` 외 블로그 상세 5개 | C1. `like_state`를 글 단위로 캐시 |
| F-003 | HIGH | INV-1 | Fix | Open(보류: F-009 결정 대기) | `blog/views/blog/blog_reply.py:74` 외 댓글 목록 8개 | C1(댓글). 댓글별 `user_auth`가 첫 요청자 기준으로 캐시됨 |
| F-004 | CRIT | INV-4 | Fix | Fixed | `blog/models/blog_reply.py:107` | C2. `post_delete`에서 지워진 행을 다시 조회해 `DoesNotExist`가 나고 삭제 전체가 롤백됨 |
| F-005 | CRIT | INV-4 | Fix | Fixed | `board/models/board_reply.py:67` | C2 형제 버그. board 댓글 3개 모델에서 같은 결함 |
| F-006 | MED | INV-5 | Fix | Open(보류: F-009 결정 대기) | `blog/views/blog/blog_reply.py:69`, `board/views/notice/notice_reply.py:71` 외 | N1. `context.post.pk`·`context.board.pk`가 댓글마다 쿼리를 냄 |
| F-007 | MED | 인수기준 M2 | Fix | Fixed | `blog/views/books/books_blog.py:21`, `blog/views/online_study/online_study_blog.py:20` | M2. 쓰지 않는 `from isort import file`. 운영에서 dev 의존성을 빼면 URLconf 로딩 실패 |
| F-008 | LOW | (계약 밖 — 승인 대기) | 미정 | Open | `blog/views/blog/blog_reply.py:38` 외 댓글 목록 8개 | 실행 중 발견. `?page` 없이 호출하면 기본값 `page=1`(int)이 캐시 키 문자열 결합에서 `TypeError` → 500. 화면 JS는 항상 `?page=`를 붙이므로(`static/js/blog_apis.js:243`) 화면 사용에는 영향 없음. 계획 밖이라 수정하지 않고 결정 대기 |
| F-009 | MED | INV-1(댓글) | 미정 | Open | `blog/views/blog/blog_reply.py:74` 외 댓글 목록 8개, `users/models.py:170-175` | 실행 중 발견. 기존 판정 `str(context.author) == request.user.username`에서 `User.__str__`은 nickname을 반환하므로 nickname≠username인 작성자는 자기 댓글의 수정·삭제 버튼을 못 본다. F-003 수정 방식이 이 결정에 달려 있어 F-003·F-006 수정을 보류 |
