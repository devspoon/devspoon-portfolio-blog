# Ledger — template-phase1-security (결함 원장)

| ID | Severity | 위반 계약 조항 | 결정 | Status | 근거 | 비고 |
|---|---|---|---|---|---|---|
| F-001 | HIGH | INV-3 | Fix | Fixed | `static/js/blog_apis.js` escapeHtml | 댓글 저장형 XSS(insertAdjacentHTML) |
| F-002 | HIGH | INV-2 | Fix | Fixed | `blog/templatetags/public_tags.py` sanitize_html, 상세 8곳 | 본문 `\|safe` 저장형 XSS(방명록·재활성화는 일반 회원 작성) |
| F-003 | HIGH | INV-1 | Fix | Fixed | Delete 16 `http_method_names=["post"]` | GET 삭제 CSRF |
| F-004 | HIGH | INV-1 | Fix | Fixed | `users/views/users.py` UserDeleteView | GET 탈퇴 CSRF + 로그인 검사 없음(비로그인 500) |
| F-005 | MED | INV-1 | Fix | Fixed | Like 5 get→post | GET 좋아요 토글 CSRF |
| F-006 | HIGH | ADR-004 | Fix | Fixed | `common/mixin/views.py` StaffRequiredMixin | 블로그 5종·공지 작성이 로그인 회원 누구나 가능 |
| F-007 | MED | 인수기준(POST 삭제 동작) | Fix | Fixed | `board/views/*/*_board.py` | 기존 버그: `post.update()` 없음 → 게시판 삭제 항상 500 |
| F-008 | MED | 인수기준 | Fix | Fixed | `blog/models/blog_reply.py`, `board/models/board_reply.py` | 기존 버그: post_delete에서 삭제된 행 재조회 → 댓글 삭제 항상 500 |
| F-009 | HIGH | 데이터 손실 | Fix | Fixed | `users/models.py` set_delete | 기존 버그: 탈퇴 시 공용 기본 이미지 `media/default/no_img.png` 삭제 |
| F-010 | MED | 인수기준 | Fix | Fixed | `users/models.py` set_delete | 기존 버그: `self.userprofile` 오타 → 탈퇴 시 500, 프로필 잔존 |
| F-011 | MED | INV-1(403 계약) | Fix | Fixed | `common/error/error_views.py` | 기존 버그: 400/403/404/500 핸들러가 모두 HTTP 200 반환 |
