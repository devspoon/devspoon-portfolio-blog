# Run Log — phase3-cache-redesign (라운드 로그 + 수렴 판정)

## 라운드 기록

### Round 0 — 2026-11-12 (base SHA: `a871122`, 브랜치 `crp/phase3-cache-redesign`)
- **트리거:** 사용자 "진행해줘"(3단계 캐시 재설계)
- **학습:** 캐시 헬퍼(`common/components/django_redis_cache_components.py`)와 호출부 전부(상세 8·댓글 8·admin mixin 4종·`index_cache_clean`·index·portfolio·템플릿 태그)를 읽음. django-redis 7.0 API 확인: `get_or_set`·`delete_many` 있음, hash는 `hset`만 있고 `hget` 없음 → 댓글 목록은 버전 토큰 방식(ADR-004)
- **재현 확인:** 게시판 댓글 모델에 `post` 속성 없음(`NoticeReply` 필드: …, `board`) → admin 댓글 저장·삭제 500(F-006)
- **결함:** F-001~F-010 등록(HIGH 4, MED 3, LOW 3)
- **수렴 판정:** `NOT CONVERGED`(설계 단계, D1·D2 결정 대기)

### Round 1 — 2026-11-12 (base SHA: `a7fa41f`, REQ-002 승인 후 실행)
- **0 기준선:** pytest 212 passed / 1 skipped. `redis-cli MONITOR`로 고정 요청 16개(8개 경로 × 미스·히트, `scanprobe.sh`) 동안 **SCAN 18 · TTL 10 · GET 40 · SET 2**. 댓글 목록 `?page` 없이 500(F-008 재현)
- **1 보호 테스트:** `common/test_phase3_cache.py` 140개. 현재 코드에서 84개 실패(전부 F-001~F-010 증상), 56개 통과(유지할 동작: JSON 형식·요청자별 값 없음 등). 실행 중 F-011 발견(index는 SQLite에서 렌더링 불가) → index 테스트는 키 무효화로 바꾸고 읽기 경로는 runserver로 확인
- **2 `b3adf1b`:** v2 키 함수, `common/cache_invalidation.py`(시그널 + `on_commit`, `HomeConfig.ready()`에서 연결), admin mixin 정리. 무효화 테스트 green, 게시판 댓글 admin `AttributeError` 사라짐
- **3 `2bad1ef`:** `ReplyListJsonMixin` + 8개 뷰, 버전 토큰 키, `page` 정규화. 1단계 쿼리 수 테스트 포함 댓글 테스트 green
- **4 `cc26066`:** `PostDetailMixin`·`BlogPostDetailMixin` + 8개 뷰, 상세 캐시 제거(D2-A), `activate_objects`(D1-A), 수동 삭제·`index_cache_clean` 제거. 실행 중 F-012 발견(게시판 삭제 뷰 `post.update` → 500), 범위 밖이라 기록만
- **5 `c727c3e`:** index·portfolio·경력 JSON·메뉴·사이트 정보를 키 1개 읽기로, 언어별 키. 테스트 파일 커밋(전체 352 passed)
- **6 `97b9c6b`:** `dredis_*`·`REDIS_CONN`·`redis_mode`·`common/decorators/cache.py` 삭제, admin의 `cache_prefix`·`cache_reply_prefix`·`use_pk`·`view_keys` 삭제. grep 0건
- **7 마무리 검증:** check exit 0, 우리 앱 No changes, pytest **352 passed / 1 skipped**. runserver 점검표 전부 통과. 같은 고정 요청 16개에서 **SCAN 0 · TTL 0 · GET 70 · SET 4**(GET은 메뉴·사이트 정보 태그가 호출마다 1회씩 20·20, `django_user_agents` 16, 나머지 index·portfolio·경력·댓글 목록 버전·페이지). 상세·댓글 목록은 `?page` 없이도 200. PostgreSQL에서: admin 숨김 → index에서 바로 사라지고 상세 404, 공개 → 다시 보임, ORM 삭제 표시 → 404·index에서 사라짐, 경력 JSON `ko`·`en`이 각 언어 행만 반환하고 삭제가 두 언어에 바로 반영
- **GATE 통과:** 0 ■ 1 ■ 2 ■ 3 ■ 4 ■ 5 □(계약 밖 신규 F-011·F-012 결정 대기)
- **수렴 판정:** `NOT CONVERGED` — 이번 범위의 Open Fix 0, INV-1~7 통과. 실행 중 발견한 F-011(LOW)·F-012(HIGH)가 사용자 결정 대기
- **검사 범위의 한계:** CI 미실행(push 안 함). 게시판 댓글 admin은 실제 화면 POST가 아니라 `save_model`·`delete_model` 테스트로 확인(R-007). index 화면 렌더링은 테스트가 아니라 runserver(PostgreSQL)로만 확인(F-011)

### Round 2 — 2026-11-12 (base SHA: `9bbb5b0`, REQ-003)
- **트리거:** 사용자 "권장안대로 수정해줘"(F-011·F-012)
- **형제 버그 검사:** 인스턴스에 `.update(`를 부르는 곳은 게시판 삭제 뷰 3곳뿐(`portfolio/tests`의 `data.update`는 dict)
- **red:** 새 테스트 8개 중 게시판 삭제 3개 `AttributeError`, index 2개와 `test_cache_holds_no_visitor_values`(index 추가) 8개 `LIMIT/OFFSET not allowed in subqueries` — 수정 전 실패 확인. 다른 사람 삭제 403 테스트 3개는 보호 테스트로 통과
- **수정:** F-012 `board/views/{notice,visiter,reactivation}/*_board.py`, F-011 `home/views/index.py`
- **검증:** check exit 0, 우리 앱 No changes, pytest **360 passed / 1 skipped**. PostgreSQL(dev DB)에서 옛 union 쿼리와 새 방식의 (게시판, pk) 목록 동일 — dev DB에는 블로그 글 3개뿐이라 여러 게시판이 섞인 경우는 SQLite 테스트가 확인
- **GATE 통과:** 0 ■ 1 ■ 2 ■ 3 ■ 4 ■ 5 ■
- **수렴 판정:** `CONVERGED` — Open Fix 0, INV-1~7 통과, 인수 기준 충족, 요구사항 회귀 0
- **검사 범위의 한계:** CI 미실행(push 안 함). 게시판 삭제는 테스트로만 확인(runserver 점검표에 없음). 잔여 위험 R-001~R-007

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
| 1 | 0 | 1 | 0 | 1 | 10 Fixed(F-001~010), 신규 2(F-011·F-012) 결정 대기 | NOT CONVERGED |
| 2 | 0 | 0 | 0 | 0 | 2 Fixed(F-011·F-012) | CONVERGED |
