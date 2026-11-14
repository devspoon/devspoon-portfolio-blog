# Charter — phase7-session-store (v0.2 / 2026-11-14)

## 1. 변경 대상
| 파일 | 변경 |
|---|---|
| `config/settings/{dev,stage,prod,test}.py` | `SESSION_ENGINE` → DB(D1), `SESSION_CACHE_ALIAS` 줄 정리 |
| `config/settings/base.py` | `SESSION_COOKIE_AGE = 1209600`(D3-A) |
| `common/core/replica_router.py` | `db_for_read`: `sessions` 앱은 `default` |
| `users/management/commands/move_sessions.py`(새, D2-A) | Redis(`default` 캐시)의 세션을 DB 행으로 옮기고 Redis 키 삭제. `--dry-run`, 다시 실행해도 안전 |
| `users/tasks.py`(추가, D4-A) | `clear_expired_sessions` Celery 작업(내장 `clearsessions` 호출) |
| `docs/crp/groups/phase7-session-store/deploy.md`(새) | 배포 순서: 코드 배포 → `migrate`(세션 테이블 확인) → (D2-A) `move_sessions` → (D4) 정리 일정 등록 |
| 테스트 | `common/test_phase7_sessions.py` |

## 2. 계약
- INV-1: 로그인 세션은 `django_session` 행으로 저장되고, Redis(일반 캐시)를 비워도 로그인이 유지된다.
- INV-2: replica가 늦어도(항상 빈 replica) 로그인 직후 GET에서 로그인 상태가 유지된다.
- INV-3: 세션 만료 시각은 마지막 요청 + D3 이내.
- INV-4: (D2-A) `move_sessions` 뒤 옮긴 세션으로 그대로 로그인돼 있고, `--dry-run`은 아무것도 바꾸지 않으며, 두 번째 실행은 옮길 것이 없다. 일반 캐시 키는 건드리지 않는다.
- INV-5: 정리 작업은 만료된 행만 지운다.
- INV-6: 전체 pytest, `check`, 이쪽 앱 migration 변경 없음, runserver 점검표(로그인 화면 포함) 통과.

## 3. 비범위
- 서버 cron·Celery beat 프로세스 운영(인프라), 배포 yml·secrets, 세션 테이블 인덱스·파티셔닝.

## 변경 이력
- v0.2 (2026-11-14): DB 저장 방식. 실행 중 명령·작업 위치를 `users` 앱으로(`common`은 설치된 앱이 아니라 명령·Celery 자동 등록이 안 된다)
