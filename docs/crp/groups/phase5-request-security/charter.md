# Charter — phase5-request-security (v0.1 / 2026-11-13)

> 상위 기준은 `design-baseline.md`.

## 1. 원인 (재현 근거)
| # | 문제 | 위치 | 영향 |
|---|---|---|---|
| P-1 | 캐시 재생성이 replica에서 읽는다. 무효화 직후 replica가 늦으면 옛 값을 24시간(`CACHE_TTL`) 캐시 | `common/components/django_redis_cache_components.py` `cached()`, `common/mixin/views/reply_list.py` | 새 댓글·글 수정이 하루 동안 안 보일 수 있음 |
| P-2 | 쓰기 트랜잭션 안의 읽기가 replica로 간다. `last_group_num` 증가 직후 다시 읽는 값은 커밋 전이라 replica에서 안 보임 | 댓글 생성 뷰 8개 | replica 지연 시 다른 댓글 두 개가 같은 `group`(스레드가 섞임) |
| P-3 | 없는·숫자 아닌 `parent` → `DoesNotExist`/`ValueError` 500 | 댓글 생성 뷰 8개 | Sentry 소음, 오류 화면 |
| P-4 | 다른 글의 댓글을 부모로 지정 가능, `depth`를 클라이언트가 정함 | 댓글 생성 뷰 8개 | 스레드 깨짐 |
| P-5 | 삭제·숨김 글에 댓글 작성 가능(`reply_count`도 증가) | 댓글 생성 뷰 8개 | phase3 D1-A와 불일치 |
| P-6 | 수정: 잘못된 JSON·키 누락 → 500, 공백 댓글로 변경 가능, 다른 글 URL로 수정 가능 | 댓글 수정 뷰 8개 | 500, 빈 댓글 |

## 2. 변경 대상
| 파일 | 변경 |
|---|---|
| `common/core/replica_router.py` | `ContextVar` 하나와 `read_primary()` 컨텍스트, `db_for_read`가 고정 중이면 `default`. 상태 변경 요청용 미들웨어 `PrimaryForWritesMiddleware` |
| `config/settings/base.py` | `MIDDLEWARE` 맨 앞쪽에 미들웨어 1줄 |
| `common/components/django_redis_cache_components.py` | `cached()`의 build·set을 `read_primary()` 안에서 |
| `common/mixin/views/reply_list.py` | 캐시 miss 때 조회를 `read_primary()` 안에서 |
| `common/mixin/views/reply_write.py`(새 파일) | `ReplyCreateMixin`·`ReplyUpdateMixin`(ADR-002~004) |
| 댓글 뷰 8개 | 생성·수정 클래스 본문을 mixin으로 교체(삭제 뷰는 그대로) |
| `config/settings/test.py` | 테스트 전용 `replica1` 별칭(빈 별도 SQLite) — "항상 늦은 replica"로 회귀 테스트 |
| 테스트 | `common/tests/test_phase5_replica.py`, `common/tests/test_phase5_reply_write.py` |

## 3. 계약
- INV-1: 라우터가 replica로 보내는 환경에서도, 상태 변경 요청 안의 읽기와 캐시 재생성은 `default`에서 한다(항상 빈 replica로 확인).
- INV-2: 일반 GET 요청의 읽기는 여전히 replica(부하 분산 유지).
- INV-3: 조작된 댓글 생성·수정 입력은 4xx이고 행·`reply_count`가 바뀌지 않는다. 500 없음.
- INV-4: 정상 댓글 흐름(생성 redirect, 대댓글 depth, 수정 JSON, 목록 JSON)은 그대로.
- INV-5: 전체 pytest 통과, `check` ERROR 0, 이쪽 앱 `makemigrations --check` No changes, runserver 점검표 통과, 요청 중 SCAN 0.

## 4. 인수 기준
- [x] P-1~P-6 각각 실패 테스트 → 수정 후 통과(fail-on-revert 7개 확인)
- [x] INV-1~5 통과

## 5. 비범위
- 글쓴이가 쓰기 직후 다음 GET에서 replica 대신 primary를 읽게 하는 고정(D1-B), 댓글 길이 상한(D2-B 선택 시), `group` SmallInteger 상한(32767), 인프라 replica 구성.

## 6. 변경 이력
- v0.1 (2026-11-13): 최초 작성.
- v0.2 (2026-11-13): 실행 결과 반영. 테스트 파일은 `common/test_phase5_*.py`(common의 기존 테스트 위치)
