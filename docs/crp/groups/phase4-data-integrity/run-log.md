# Run Log — phase4-data-integrity (라운드 로그 + 수렴 판정)

## 라운드 기록

### Round 0 — 2026-11-13 (base SHA: `d91fcb9`, 브랜치 `crp/phase4-data-integrity`)
- **트리거:** 사용자 "진행해줘"(4단계 데이터 정합성)
- **학습:** `table_name` 쓰기 3경로(뷰·admin·모델 기본값)와 읽기 1곳(검색 템플릿) 확인. 좋아요 연결 모델 5개 제약 없음, 토글 뷰의 잠금이 빈 결과를 잠그는 구조 확인. migration 파일은 git 무시(서버에서 생성) → 정리는 관리 명령으로(기존 `dedupe_connection_stats` 형식)
- **재현:** dev DB 블로그 글 16개 `table_name` 전부 빈 값(ORM 생성) → 검색 링크 없음
- **결함:** F-001~F-003(MED 3)
- **수렴 판정:** `NOT CONVERGED`(설계 단계, D1·D2 결정 대기)

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
