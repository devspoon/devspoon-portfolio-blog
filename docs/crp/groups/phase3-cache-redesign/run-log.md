# Run Log — phase3-cache-redesign (라운드 로그 + 수렴 판정)

## 라운드 기록

### Round 0 — 2026-11-12 (base SHA: `a871122`, 브랜치 `crp/phase3-cache-redesign`)
- **트리거:** 사용자 "진행해줘"(3단계 캐시 재설계)
- **학습:** 캐시 헬퍼(`common/components/django_redis_cache_components.py`)와 호출부 전부(상세 8·댓글 8·admin mixin 4종·`index_cache_clean`·index·portfolio·템플릿 태그)를 읽음. django-redis 7.0 API 확인: `get_or_set`·`delete_many` 있음, hash는 `hset`만 있고 `hget` 없음 → 댓글 목록은 버전 토큰 방식(ADR-004)
- **재현 확인:** 게시판 댓글 모델에 `post` 속성 없음(`NoticeReply` 필드: …, `board`) → admin 댓글 저장·삭제 500(F-006)
- **결함:** F-001~F-010 등록(HIGH 4, MED 3, LOW 3)
- **수렴 판정:** `NOT CONVERGED`(설계 단계, D1·D2 결정 대기)

## 작업 계획 (승인 후 실행 — 순서 고정)

각 하위 단계는 같은 절차를 따른다: 실패 테스트 먼저(red) → 수정(green) → `verify.sh`(INV-1~3) → 하위 단계별 커밋. 계획 밖 수정이 필요하면 고치기 전에 멈추고 묻는다.

| 순서 | 하위 단계 | 내용 | 다루는 결함 |
|---|---|---|---|
| 0 | 기준선 | `verify.sh` 212 passed, runserver 점검표, `redis-cli MONITOR`로 지금 SCAN 횟수 기록 | — |
| 1 | 보호 테스트 | 지금 동작 중 유지할 것(상세 200·이웃 글·댓글 JSON 형식·portfolio·index 내용)을 특성화 테스트로 고정. SCAN 감시 fixture | 안전망 |
| 2 | 캐시 모듈 + 무효화 | 새 키 함수·읽기 함수, `common/cache_invalidation.py` 시그널 + `on_commit`, admin mixin 정리(일괄 액션 무효화, `obj.post` 오류 제거) | F-003·F-004·F-005·F-006·F-009 |
| 3 | 댓글 목록 | `ReplyListJsonMixin` + 8개 뷰, 버전 토큰 키, `page` 정규화, 댓글 CRUD 뷰의 수동 삭제 제거 | F-002(일부)·F-008·F-010 |
| 4 | 상세 | `PostDetailMixin` + 8개 뷰, D1·D2 결정 반영 | F-001·F-002(일부)·F-010 |
| 5 | index·portfolio·메뉴 | 키 1개 읽기, 언어별 키 | F-002·F-007 |
| 6 | 정리 | `dredis_*`·`index_cache_clean` 삭제, grep 0건, 1단계 테스트의 옛 키 확인을 새 키로 | F-010 |
| 7 | 마무리 | `verify.sh`, runserver 점검표 + `MONITOR` SCAN 0회, 수렴 판정, 문서 | — |

## 심각도 추세
| Round | CRIT | HIGH | MED | LOW | 신규 Fix | 판정 |
|---|---|---|---|---|---|---|
| 0 | 0 | 4 | 3 | 3 | 10 | NOT CONVERGED(설계) |
