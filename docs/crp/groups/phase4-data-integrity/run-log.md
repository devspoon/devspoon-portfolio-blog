# Run Log — phase4-data-integrity (라운드 로그 + 수렴 판정)

## 라운드 기록

### Round 0 — 2026-11-13 (base SHA: `d91fcb9`, 브랜치 `crp/phase4-data-integrity`)
- **트리거:** 사용자 "진행해줘"(4단계 데이터 정합성)
- **학습:** `table_name` 쓰기 3경로(뷰·admin·모델 기본값)와 읽기 1곳(검색 템플릿) 확인. 좋아요 연결 모델 5개 제약 없음, 토글 뷰의 잠금이 빈 결과를 잠그는 구조 확인. migration 파일은 git 무시(서버에서 생성) → 정리는 관리 명령으로(기존 `dedupe_connection_stats` 형식)
- **재현:** dev DB 블로그 글 16개 `table_name` 전부 빈 값(ORM 생성) → 검색 링크 없음
- **결함:** F-001~F-003(MED 3)
- **수렴 판정:** `NOT CONVERGED`(설계 단계, D1·D2 결정 대기)

### Round 1 — 2026-11-13 (base SHA: `b712c6c`, REQ-002·REQ-003)
- **0 기준선:** pytest 360 passed / 1 skipped(코드 `d91fcb9`와 동일)
- **1 테스트(red):** `blog/tests/test_phase4_data_integrity.py`. 현재 코드에서 31개 실패: 중복 좋아요 허용 5, 어긋난 count 미복구 5, `save()` 정규화 없음 8, 검색 13 — 검색은 F-001이 아니라 SQLite의 union 정렬 오류(F-004)로 실패 → 계획 밖이라 멈추고 확인 요청
- **2 `2e0d64b`:** 좋아요 `UniqueConstraint` 5개, 토글은 글 행 잠금 + 실제 행 수 저장. 로컬 `makemigrations blog` → `AddConstraint` 5개만(git 무시 파일)
- **3 `722fc2f`:** `fix_data_integrity`. 테스트 DB엔 이미 제약이 있어 중복 생성 불가 → 중복 고르기는 함수 단위 테스트, 실제 삭제는 리허설로 확인. 설계 정정: 이 명령이 바꾸는 값(`like_count`·`table_name`)은 캐시된 화면에 없어 캐시 무효화 불필요(C-7의 "index 직접 무효화"는 해당 없음)
- **4 리허설(dev PostgreSQL, `blog.0003` 미적용 상태):** 중복 3+1행·count 1·`table_name` 빈 값 16 → dry-run(무변경) → 실행(중복 2·count 1·table_name 16) → 재실행 0건 → `makemigrations` 변경 없음 → `migrate` OK → 중복 삽입 `IntegrityError`. `deploy.md` 작성
  - 동시 요청 확인 중 발견: 라우터가 읽기를 replica로 보내 잠금 트랜잭션 안의 확인·count가 자기 변경을 못 봄(동시 10·11개에서 행/count 0/1·1/0). 승인된 F-003 설계를 동작하게 하는 보완으로 `4f8127c`(두 읽기를 default로). 이후 10·11·30개 → 0/0·1/1·0/0, 전부 200
  - 환경: 로컬 8000은 VS Code, 8765는 다른 WSL 컨테이너 중계가 사용 중 → 둘 다 건드리지 않고 18765 사용. 8765로 잘못 보낸 요청의 302·500은 그 서비스의 응답이었고 결과에서 제외
- **5 `2bfe36f`(REQ-003):** F-004 `.order_by()` → 검색 테스트가 F-001 증상으로 실패함을 확인 → F-001(검색 `board_type`, 템플릿, 모델 `save()`, 직접 대입 제거)
- **마무리 검증:** check exit 0, `makemigrations --check` No changes(제약 migration은 로컬 생성됨), pytest **402 passed / 1 skipped**. runserver(PostgreSQL) 점검표 전부 통과, `table_name=blog_post`인 글의 검색 링크 1/1, `phase1` 검색 10/10
- **GATE 통과:** 0 ■ 1 ■ 2 ■ 3 ■ 4 ■ 5 ■
- **수렴 판정:** `CONVERGED` — Open Fix 0, INV-1~5 통과, 인수 기준 충족, 요구사항 회귀 0
- **검사 범위의 한계:** CI 미실행(push 안 함). 운영 DB 반영은 사용자가 deploy.md로 실행. replica 관련 좋아요 동작은 dev PostgreSQL 동시 요청으로만 확인(테스트 설정엔 라우터 없음)

## 작업 계획 (승인 후 실행 — 순서 고정)

각 단계: 실패 테스트 먼저(red) → 수정(green) → 전체 검증 → 단계별 커밋. 계획 밖 수정이 필요하면 고치기 전에 멈추고 묻는다.

| 순서 | 단계 | 내용 | 결함 |
|---|---|---|---|
| 0 | 기준선 | pytest 360 passed, 검색 결과 링크 상태 기록 | — |
| 1 | 검색 링크 | 테스트(뷰·admin·ORM·복사로 만든 글이 검색에서 링크를 가짐) → `board_type` 주석·템플릿 → `save()` 정규화·직접 대입 제거 | F-001 |
| 2 | 좋아요 제약·토글 | 테스트(중복 생성 `IntegrityError`, 토글 반복 시 행 0/1·count 일치, 이미 좋아요 상태에서 추가 재요청 500 아님) → `UniqueConstraint` 5개 → 글 행 잠금 토글 | F-002·F-003 |
| 3 | 정리 명령 | 테스트(중복 정리·가장 이른 행 유지·`like_count` 재계산·`table_name` 맞춤·dry-run 무변경·재실행 무변경) → `fix_data_integrity` | F-002 |
| 4 | 운영 리허설 | dev DB(PostgreSQL)에서: 제약 migration 전 상태로 중복 데이터를 넣고 deploy.md 순서 그대로 실행, 결과 기록. deploy.md 작성 | ADR-005 |
| 5 | 마무리 | 전체 검증, runserver(검색·좋아요), 수렴 판정, 문서 | — |

## 심각도 추세
| Round | CRIT | HIGH | MED | LOW | 신규 Fix | 판정 |
|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 3 | 0 | 3 | NOT CONVERGED(설계) |
| 1 | 0 | 0 | 3 | 1 | 4 Fixed(F-001~F-004) | CONVERGED |
