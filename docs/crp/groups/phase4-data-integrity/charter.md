# Charter — phase4-data-integrity  (Charter v0.1 / 2026-11-13)

> 상위 기준은 `design-baseline.md`.

## 1. 인벤토리

### 1-1. 코드 수정 예정 파일

| 파일 | 이유 |
|---|---|
| `home/views/service/search.py` | 쿼리마다 `board_type=Value(model.__name__)` (ADR-001) |
| `templates/base/search_result_board_list.html` | `item.table_name` → `item.board_type` 8곳 (ADR-001) |
| `blog/models/blog.py`(`PostMixin.save`), `board/models/board.py`(`BoardMixin.save`) | 저장 시 `table_name`을 클래스 이름으로 (ADR-001) |
| `blog/admin/*_admin.py` 5개, `board/admin/*_admin.py` 3개, `blog/views/*/*_blog.py` 5개, `board/views/*/*_board.py` 3개 | `table_name` 직접 대입 제거 (ADR-001) |
| `blog/models/like.py` | `UniqueConstraint` 5개 (ADR-002) |
| `blog/views/*/*_blog.py` 5개 `*LikeJsonView` | 글 행 잠금 후 토글 (ADR-003) |
| `blog/management/commands/fix_data_integrity.py`(신규) | 정리 명령 (ADR-004) |
| `docs/crp/groups/phase4-data-integrity/deploy.md`(신규) | 운영 반영 순서 (ADR-005) |
| 신규 테스트 `blog/tests/test_phase4_data_integrity.py` | 아래 불변식 |

## 2. 계약
### 2-1. 지원 구성
- Python 3.12, `config.settings.test`(SQLite + Redis)로 pytest, `config.settings.dev`(PostgreSQL + Redis)로 명령·runserver 확인.
### 2-2. 위협 모델
- 방어한다: 작성 경로에 따라 검색 링크가 빠지는 것, 좋아요 중복 저장과 `like_count` 어긋남, 정리 명령이 남겨야 할 행을 지우는 것.
- 방어하지 않는다: 운영 DB 반영 자체(사용자가 deploy.md 순서대로 실행), 다른 사용자의 좋아요 대리 실행(5단계 GET→POST).
### 2-3. 불변식
- INV-1: 검색(키워드·태그) 결과의 모든 행이 그 글의 상세 링크를 가진다. 글을 뷰·admin·ORM·admin 복사 중 어느 경로로 만들었든 같다.
- INV-2: 좋아요 연결 모델마다 (users, 글)은 유일하다(DB 제약).
- INV-3: 좋아요 토글을 같은 사용자가 몇 번 하든 행 수는 0 또는 1이고 `like_count`는 행 수와 같다. 이미 좋아요한 상태에서 추가가 다시 와도 500이 아니다.
- INV-4: `fix_data_integrity`는 여러 번 실행해도 두 번째부터 바꾸는 것이 없고, `--dry-run`은 아무것도 바꾸지 않는다. 중복이 없는 좋아요 행은 지우지 않는다.
- INV-5: 전체 pytest 통과, `manage.py check` ERROR 없음, `makemigrations --check`는 blog `AddConstraint` 5개만.
### 2-4. 비목표
- `table_name` 컬럼 삭제(스키마 변경 최소화), 좋아요 GET→POST(5단계), 태그 검색 페이지 나눔(6단계 M4).

## 3. 인수 기준
- [ ] F-001~F-003 Fixed, 각 수정에 수정 전 실패한 테스트가 있다
- [ ] INV-1~5 통과
- [ ] dev DB(PostgreSQL)에서: 중복 좋아요를 만들어 `--dry-run` → 실행 → 재실행(변경 0) → `makemigrations blog`·`migrate` 성공 → 이후 중복 삽입이 `IntegrityError`
- [ ] runserver: 검색 결과에 admin·ORM으로 만든 글의 링크가 나온다, 좋아요 토글 정상
- [ ] deploy.md 작성
- [ ] 불가침 제약 C-1~C-7 위반 없음

## 4. 변경 이력
- v0.1 (2026-11-13): 최초 작성.
