# Design Baseline — phase4-data-integrity (기준 설계 문서)

> 이 그룹의 요구사항·설계 결정의 단일 기준. append-only.

## 0. 질의 수준 (Autonomy Level)

- [x] **적극(Thorough)**
- [ ] 보통(Balanced)
- [ ] 간략(Lean)

선택: **적극** · 선택일: 2026-11-13 · 변경 이력: 없음

> 사용자 규칙: 설계·작업 계획 승인 후 실행. 실행 중 계획 밖 수정이 필요하면 고치기 전에 멈추고 묻는다. 커밋만 하고 push·병합·배포는 하지 않는다. 인프라(nginx·gunicorn·서버)는 고려하지 않는다.

## 1. 목적 / 배경

첫 검수의 데이터 정합성 항목 두 가지를 고친다.
1. **M1 `table_name`:** 검색 결과는 여러 게시판을 `union`으로 합치고, 각 행이 어느 게시판 글인지를 저장된 `table_name`으로 판단해 링크를 만든다(`templates/base/search_result_board_list.html:43-65`). 그런데 이 값을 넣는 경로마다 값이 다르다.
2. **좋아요 중복:** 좋아요 연결 모델 5개에 (사용자, 글) unique 제약이 없다. 좋아요 뷰는 행이 없을 때 잠글 대상이 없어 동시 요청 두 개가 모두 "없음"을 보고 둘 다 추가할 수 있다.

> 이 프로젝트는 migration 파일을 저장소에 두지 않고 서버에서 `makemigrations`로 만든다(`.gitignore`). 그래서 데이터 정리는 migration이 아니라 관리 명령으로 하고, 제약은 모델 `Meta`에 선언해 서버 `makemigrations`가 만들게 한다. 기존 `dedupe_connection_stats` 명령과 같은 형식이다.

## 2. 요구사항 레지스터

| Req-ID | 날짜 | 요청(원문 요약) | 도출된 요구사항 | 상태 | 연결 |
|---|---|---|---|---|---|
| REQ-001 | 2026-11-13 | "진행해줘"(다음 단계 = 4단계 데이터 정합성: M1 `table_name`, 좋아요 unique) | 검색 결과의 모든 글에 올바른 링크가 나온다(작성 경로와 무관). 좋아요는 (사용자, 글)당 1개만 저장되고 `like_count`가 실제 좋아요 수와 같다. 운영 DB 반영 절차(백업→정리→migration)를 문서로 남긴다. | Active | ADR-001~005 |

## 3. 설계 결정 기록 (ADR)

| ADR-ID | 날짜 | 결정 | 근거 | 상태 | supersedes |
|---|---|---|---|---|---|
| ADR-001 | 2026-11-13 | **(D1 결정 대기)** 권장 A: 검색은 저장된 `table_name`을 읽지 않고, 쿼리마다 그 모델 이름을 `Value(model.__name__)`로 붙여(`board_type`) 템플릿이 그 값을 쓴다. 저장 값은 모델 `save()`가 항상 클래스 이름으로 맞추고, 뷰·admin의 직접 대입은 없앤다. 기존 행은 검색에 영향이 없으므로 고칠 필요가 없지만, 같은 명령(ADR-004)에서 한 번에 맞춘다. | 지금 값의 출처가 셋이고 모두 다르다: 뷰 `model.__name__`(`BlogPost`), admin `_meta.db_table`(DB 테이블 이름), ORM·shell·admin 복사 등은 빈 값이나 게시판 기본값 `default=__name__`(모듈 이름 `board.models.board`). dev DB의 블로그 글 16개가 전부 빈 값이다. 저장 값에 기대지 않으면 배포 즉시, 데이터 정리 없이 모든 글이 링크를 갖는다. B(저장 값만 바로잡고 정리 명령으로 기존 행을 고침)는 정리 전까지 링크가 빠지고, 새 쓰기 경로가 생기면 다시 깨질 수 있다. | Proposed | — |
| ADR-002 | 2026-11-13 | 좋아요 연결 모델 5개(`ProjectLike`·`OnlineStudyLike`·`BlogLike`·`OpenSourceLike`·`BooksLike`)의 `Meta`에 `UniqueConstraint(fields=["users", <글 FK>])`를 추가한다. 컬럼·nullable 설정은 바꾸지 않는다. | 중복 방지는 DB 제약이 최종 방어선이다. PostgreSQL에서 NULL은 서로 다른 값으로 취급돼 NULL 행이 있어도 제약 추가가 실패하지 않는다. | Proposed | — |
| ADR-003 | 2026-11-13 | **(D2 결정 대기)** 권장 A: 좋아요 토글 뷰 5개는 먼저 글 행을 `select_for_update()`로 잠근 뒤 좋아요 여부를 확인한다. 같은 글에 대한 토글이 순서대로 처리돼 중복 추가·잘못된 증감이 생기지 않는다. | 지금은 좋아요 행을 잠그는데, 행이 없을 때는 잠글 것이 없다. 제약만 추가하면 빠른 두 번 클릭의 두 번째 요청이 `IntegrityError`(500)가 된다. 원래 5단계(요청 처리 보안)의 "좋아요 race"였지만 제약과 붙어 있어 함께 하는 편이 안전하다. B: 제약만 추가하고 토글은 5단계에서. | Proposed | — |
| ADR-004 | 2026-11-13 | 관리 명령 `fix_data_integrity`(`blog/management/commands/`)를 추가한다. ① 좋아요 (사용자, 글) 중복은 가장 먼저 만든 행 1개만 남기고 지운다 ② 모든 블로그 글의 `like_count`를 실제 좋아요 행 수로 다시 계산한다 ③ 모든 글(블로그 5·게시판 3)의 `table_name`을 클래스 이름으로 맞춘다. `--dry-run`을 지원하고, 여러 번 실행해도 결과가 같고, 모델마다 트랜잭션으로 처리한다. `update()`로 쓰므로 `updated_at`은 바뀌지 않는다. | 제약 migration은 중복이 있으면 실패하므로 그 전에 정리해야 한다. `like_count`는 이미 중복 추가·삭제로 실제 수와 어긋났을 수 있다(사용자에게 보이는 숫자가 바로잡힘, C-3). | Proposed | — |
| ADR-005 | 2026-11-13 | 운영 반영 순서를 문서로 남긴다: DB 백업 → 코드 배포 → `fix_data_integrity --dry-run`으로 확인 → `fix_data_integrity` → `makemigrations blog`(좋아요 제약 5개 생성 확인) → `migrate`. 이 순서와 되돌리기 방법을 `docs/crp/groups/phase4-data-integrity/deploy.md`에 쓴다. | migration을 서버에서 만들기 때문에 정리와 migration 사이에 사람이 실행할 단계가 생긴다. 배포·운영 실행은 사용자가 한다(phase1 REQ-002). | Proposed | — |

## 4. 불가침 제약

- C-1: 기존 테스트(360 passed / 1 skipped)가 통과한다. 지우거나 skip해서 통과시키지 않는다. — REQ-001
- C-2: 스키마 변경은 좋아요 제약 5개(ADR-002)뿐이다. `makemigrations --check`는 blog 앱의 `AddConstraint` 5개만 보여야 하고, 다른 앱은 No changes. — REQ-001
- C-3: 사용자에게 보이는 동작 변경은 검색 결과 링크가 모든 글에 나오는 것, `like_count`가 실제 수로 바로잡히는 것, 좋아요 연타가 중복을 만들지 않는 것뿐이다. — REQ-001
- C-4: 인프라 파일은 바꾸지 않는다. 운영 DB에서 명령을 실행하지 않는다(문서만). — phase1 REQ-003
- C-5: 커밋만 하고 push·병합하지 않는다. PR을 쓰지 않는다. — phase1 REQ-002
- C-6: WSL의 다른 컨테이너와 로컬 DB 백업은 건드리지 않는다. 로컬 검증은 `devspoon-postgres` 컨테이너의 dev DB에서만 한다. — phase1 C-7
- C-7: 3단계 캐시 불변식 유지: 쓰기 뒤 무효화는 시그널·`on_commit`(관리 명령의 `update()`는 index 캐시를 직접 무효화한다). — phase3 INV-6

## 5. 변경 이력

- v0.1 (2026-11-13): 최초 작성(REQ-001, ADR-001~005 Proposed, D1·D2 결정 대기).
