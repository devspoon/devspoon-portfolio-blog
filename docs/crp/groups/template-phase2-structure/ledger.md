# Ledger — template-phase2-structure (결함 원장)

| ID | Severity | 위반 계약 조항 | 결정 | Status | 근거 | 비고 |
|---|---|---|---|---|---|---|
| F-001 | MED | ADR-004 | Fix | Fixed | `templates/blog/_post_detail.html` | books 계열 이전·다음 글이 잘못된 글로 이동(JS ±1 재계산) |
| F-002 | MED | ADR-003 | Fix | Fixed | `templates/board/board_list.html` | 방명록·재활성화 목록의 번호 링크가 공지 상세로 이동(`board:notice_detail` 고정) |
| F-003 | LOW | ADR-003 | Fix | Fixed | 목록 2종·검색 + ListView 8 `extra_context` | `<title>` "title", 제목이 JS 의존 → 서버 렌더링(문구 동일) |
| F-004 | LOW | ADR-007 | Fix | Fixed | `templates/base/post_form.html` | 수정 폼 머리말 "OpenSource" 복붙(4종), 취소→로그인, "Cancle" |
| F-005 | LOW | ADR-005 | Fix | Fixed | `meta.html`, `base.html` | `<title>` 2개, `<main>` 없음 |
| F-006 | LOW | ADR-005 | Fix | Fixed | `mobile_menu.html`, `pagenation.html`, 상세 | 중복 속성·중첩 링크 소스, 짝 없는 `</h1>`·`</span>`, `<a><h4>` |
| F-007 | LOW | ADR-005 | Fix | Fixed | login·profile·index·portfolio·list | img alt 7 |
| F-008 | MED | C-2(회귀) | Fix | Fixed | `post_form.html` | **실행 중 회귀**: 공지 작성 폼 priority/sorting 초기값 0 사라짐 → 픽셀 비교로 발견, `field.initial` 복원 + 테스트 |
| F-009 | MED | C-2(회귀) | Fix | Fixed | `password_replacement.html` | **실행 중 회귀**: `<a class="btn">` 전환 시 Cancel이 테마색→파랑(`section.first button.btn`) → 원 마크업 복원 |

## 발견했으나 고치지 않은 기존 결함 (계획 밖 — 사용자 결정 필요)
| ID | 내용 | 위치 |
|---|---|---|
| X-001 | 상세 뷰가 `user_auth`(요청 사용자)·`like_state`를 글 단위 Redis 캐시에 저장 → 다른 방문자에게 첫 방문자의 값 사용, 비로그인에도 수정·삭제 버튼 노출 가능(서버 권한 검사는 1단계에서 차단) | `blog/views/*/*_blog.py`, `board/views/*/*_board.py` DetailView |
| X-002 | 블로그 목록 저장소 링크 `<a ref=...>`(href 오타) → 클릭 불가 | `templates/blog/blog_list.html` |
| X-003 | 댓글 수정 버튼은 onclick 지정 전 클릭 시 폼 submit(현 동작 유지, type 명시만) | `templates/base/reply.html` |
| X-004 | Summernote JS가 jQuery 없이 전역 로드되어 모든 페이지 콘솔 오류 | `templates/base/javascripts.html` (4단계) |
| X-005 | `pre_board`/`next_board`가 삭제된 글도 포함(`objects` 사용) | 상세 뷰 |
| X-006 | 수정 폼 파일 링크 `{{ field.url }}` 미존재 속성 → href 빈 값 | `templates/base/post_form.html` (원본 동작 유지) |
