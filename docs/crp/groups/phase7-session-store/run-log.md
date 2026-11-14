# Run Log — phase7-session-store

## 작업 계획 v0.2 (승인됨)
| 순서 | 단계 |
|---|---|
| 1 | 실패 테스트: 세션이 DB 행, 캐시 비워도 로그인 유지, 항상 빈 replica에서 로그인 직후 GET 유지, 수명 2주, (D2-A) 옮기기 명령, (D4-A) 정리 작업 |
| 2 | 설정 4곳·base, 라우터 |
| 3 | (D2-A) `move_sessions`, (D4-A) 정리 작업 |
| 4 | fail-on-revert, 전체 pytest·check·migration |
| 5 | runserver(PostgreSQL): 로그인 → Redis 비우기 → 로그인 유지, Redis에 만든 옛 세션 옮기기 리허설, 정리 작업 실행 |
| 6 | 배포 문서·커밋(push 안 함) |

## 라운드 로그
- 2026-11-14 v0.1(Redis DB 번호 분리안) 작성 → 사용자 요청(REQ-003)으로 v0.2(DB 저장)로 재설계. 코드 변경 없음

### Round 1 — 2026-11-14 (브랜치 `crp/phase7-session-store`, `394c23c` 위)
- **트리거:** 사용자 "권장하는 방법으로 진행해줘"(D1~D4 모두 A)
- **red:** 새 테스트 5개, 정리 작업이 없어 수집 단계 실패
- **실행 중 조정:** 명령·Celery 작업은 `users` 앱에(`common`은 설치된 앱이 아님). replica 테스트는 사용자 행만 replica에 미리 복사(실제로는 오래전에 복제돼 있음) — "세션만 아직 복제 전" 상황을 재현
- **green:** 5 passed. fail-on-revert 6건(DB 엔진, 세션 primary 읽기, 수명 2주, 옮긴 뒤 Redis 키 삭제, dry-run, 정리 작업) 각각 실패 확인
- **게이트:** pytest **750 passed / 1 skipped**, check exit 0, 이쪽 앱 `makemigrations --check` No changes
- **dev 리허설(PostgreSQL·로컬 Redis·runserver):** 옛 Redis 세션 → 옮기기 전 프로필 302(로그아웃 상태) → `move_sessions --dry-run` 1개 예정 → 실행 1개 이동 → 재실행 0개 → 프로필 200 → Redis DB 0 FLUSHDB 뒤에도 200 → 만료까지 14.0일 → 정리 작업이 만료 행만 삭제. 기존 점검표·5단계 댓글 점검 통과(점검용 시드 스크립트가 Redis 세션을 직접 만들던 것을 설정된 엔진으로 바꿈), 500 0건
- **수렴 판정:** `CONVERGED` — Open Fix 0
- **검사 범위의 한계:** 운영 MySQL에서는 실행하지 않음(배포 문서대로 사용자가). Celery beat 일정은 등록하지 않음(admin에서 사용자가). CI 미실행
