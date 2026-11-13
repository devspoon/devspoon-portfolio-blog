# Ledger — phase4-data-integrity (결함 원장)

| ID | Severity | 위반 계약 조항 | 결정 | Status | 근거 | 비고 |
|---|---|---|---|---|---|---|
| F-001 | MED | INV-1 | Fix(ADR-001, D1) | Open | `blog/admin/*_admin.py:43-44`, `board/admin/*_admin.py:41`(`obj.table_name = obj._meta.db_table`), `blog/views/*/*_blog.py:54`·`board/views/*/*_board.py:54`(`model.__name__`), `board/models/board.py:50`(`default=__name__`) | 첫 검수 M1. admin에서 저장한 글은 `table_name`이 DB 테이블 이름이라 검색 템플릿의 조건(`'BlogPost'` 등)에 맞지 않아 제목 링크가 빠진다. ORM·shell·admin 복사로 만든 글은 빈 값이거나 게시판 기본값(모듈 이름 `board.models.board`)이다. dev DB 블로그 글 16개 전부 빈 값 |
| F-002 | MED | INV-2 | Fix(ADR-002·004) | Open | `blog/models/like.py`(5개 모델, Meta에 제약 없음) | 첫 검수 "좋아요 unique". (users, 글) 중복 행이 DB에 들어갈 수 있다. 중복이 있으면 취소할 때 `remove()`가 둘 다 지우지만 `like_count`는 1만 줄어 실제 수와 어긋난다 |
| F-003 | MED | INV-2·INV-3 | Fix(ADR-003, D2) | Open | `blog/views/*/*_blog.py` `*LikeJsonView.get` | 좋아요 행을 `select_for_update`로 잠그는데 행이 없을 때는 잠글 대상이 없다. 같은 사용자의 동시 요청 두 개가 모두 "없음"을 보고 둘 다 추가·증가할 수 있다(F-002의 원인). 제약만 추가하면 두 번째 요청이 `IntegrityError`(500) |
