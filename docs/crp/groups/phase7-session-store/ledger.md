# Ledger — phase7-session-store (결함 원장)

| ID | Severity | 항목 | 결정 | Status | 근거 |
|---|---|---|---|---|---|
| F-001 | MED | 세션이 일반 캐시와 같은 Redis 공간 — 캐시 비우기·Redis 재시작·축출이 전원 로그아웃 | Fix(ADR-001) | Fixed | design-baseline §1 |
| F-002 | MED | 세션 서버 수명 68년 — 로그아웃 안 한 세션이 영원히 쌓인다 | Fix(ADR-003·004) | Fixed | 실측 TTL 2147483647 |
| F-003 | MED | (DB 방식으로 바꾸면 생기는 문제) 세션 읽기가 replica로 가 로그인 직후 로그아웃처럼 보일 수 있다 | Fix(ADR-002) | Fixed | `django/contrib/sessions/backends/db.py:34` |
