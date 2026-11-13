# Ledger — phase5a-integration (결함 원장)

| ID | Severity | 위반 계약 조항 | 결정 | Status | 근거 | 비고 |
|---|---|---|---|---|---|---|
| F-001 | HIGH | C-1(실행 중 import 오류) | Fix(ADR-004) | Fixed | 그쪽 `common/mixin/views.py` ↔ 이쪽 `common/mixin/views/` | git 충돌로 잡히지 않는 이름 충돌. 패키지가 우선해 그쪽 `from common.mixin.views import StaffRequiredMixin`이 실패했을 것. `StaffRequiredMixin`을 패키지 `__init__.py`로 옮기고 모듈 삭제. `apply_viewer_state`·`VIEWER_KEYS`는 이쪽 상세 mixin과 같은 일을 해 쓰지 않음 |
| F-002 | MED | 이쪽 phase3 INV-6 | Fix(ADR-001) | Fixed | `portfolio/views.py`(그쪽 `stack`·`experience`), `common/cache_invalidation.py` | 그쪽이 portfolio 캐시에 넣은 기술 스택 글 수는 블로그 글·태그에 따라 바뀌는데, 이쪽 무효화 대상은 portfolio 모델과 ProjectPost뿐이었다. 블로그 글 5종을 portfolio 무효화 대상에 넣고 `tag_set` `m2m_changed`도 연결. 테스트 `test_portfolio_stack_refreshes_after_tagging_and_hiding_a_post`(새 무효화를 빼면 실패 확인) |
| F-003 | MED | 이쪽 phase4 INV-1 | Fix(ADR-002) | Fixed | `templates/base/search_result_board_list.html`(그쪽 새 템플릿) | 그쪽 새 검색 템플릿은 `table_name` 7개 비교 + `else`(책)라 `table_name`이 틀린 글은 링크가 빠지는 대신 책 게시판 주소로 잘못 연결됐다. `board_type`으로 교체 |
| F-004 | MED | 이쪽 계약(문의 폼 보안) | Fix(ADR-002) | Fixed | `templates/portfolio/portfolio.html`(그쪽 새 문의 폼) | 그쪽 새 폼에 reCAPTCHA 위젯과 입력 길이 제한·필수 표시(이쪽 sentry 브랜치 반영분)가 빠져 있었다. 새 마크업에 다시 넣음 |
| F-005 | LOW | C-1 | Fix | Fixed | 이쪽 테스트 17개 | 그쪽 승인 계약에 맞춰 요청 방식만 갱신: 좋아요 10개 GET→POST(그쪽 ADR-001), 작성 화면 5개 staff 사용자(그쪽 ADR-004), 에러 화면 2개 새 제목 `404 \| devspoon`(그쪽 디자인). 확인하는 내용은 그대로 |
| F-006 | — | (동작 결정 승계) | Accept | Accepted | `home/views/index.py`, `common/test_phase3_cache.py` | 그쪽 STOP 2 결정(홈은 최신 글부터, `author` 필드 제외)을 이쪽 구조(캐시 v2·Python 합치기)에 반영. 이쪽은 원래 정렬을 유지했을 뿐 다른 결정이 없어 ADR-006(충돌 시 질문) 대상 아님. index 테스트를 최신순으로 갱신 |
| F-007 | MED | ADR-006(양쪽 결정 충돌) | Fix(ADR-007, 사용자 B안) | Fixed | 댓글 뷰 8개, `static/js/modules/comments.js`, `templates/components/comments.html`, `blog/tests/test_detail_cache.py` | 그쪽 `61776e9`는 댓글 JSON에 `author_id`를 넣고 JS가 판단했고, 이쪽은 서버가 `user_auth`를 계산했다. 뷰 8개는 이쪽 mixin 유지(그쪽의 `page` 기본값 `"1"`은 이쪽 `page_number()`가 이미 처리). JS 판단 1줄과 `data-viewer` 제거. 그쪽 테스트 `test_reply_list_is_viewer_neutral`은 같은 캐시를 읽어도 작성자 `true`·익명 `false`, `author_id` 없음으로 갱신 |
