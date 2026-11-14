# Residual Risk — phase7-session-store

| ID | 항목 | Severity | 왜 비범위인가 | 수용일 | 재평가 조건 |
|---|---|---|---|---|---|
| R-001 | 로그인 사용자의 요청마다 세션 읽기 1회(PK 조회)와 저장 1회(UPDATE)가 primary DB에 생긴다(`SESSION_SAVE_EVERY_REQUEST`). 비로그인 방문은 세션이 없어 영향 없음 | LOW | 블로그 특성상 로그인 사용자가 적다. `cached_db`(D1-B)로 읽기는 줄일 수 있다 | — | DB 부하가 보이면 |
| R-002 | 정리 일정(D4)이 실제로 돌지 않으면 만료 행이 쌓인다 | LOW | Celery beat·cron 운영은 인프라 | — | 배포 후 `django_session` 행 수 확인 |
| R-003 | 운영 DB에 `django_session` 테이블이 있는지 저장소에서 확인할 수 없다 | LOW | 서버 DB | — | 배포 문서의 `migrate` 단계에서 확인 |
