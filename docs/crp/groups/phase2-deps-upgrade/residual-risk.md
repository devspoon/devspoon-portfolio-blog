# Residual Risk — phase2-deps-upgrade (잔여 위험 등록부)

| ID | 항목 | Severity | 왜 비범위인가 | 수용일 | 재평가 조건 |
|---|---|---|---|---|---|
| R-001 | 운영 서버의 Python이 3.12 미만이면 배포 후 동작하지 않는다 | HIGH | 인프라는 고려하지 않는다(phase1 REQ-003). 배포 워크플로는 별도 저장소의 docker 구성을 쓴다 | 2026-11-12 | 서버 배포를 요청받으면 그 전에 서버 Python 버전을 확인한다 |
| R-002 | Django 6.x로 올리지 않고 5.2 LTS에 머문다 | LOW | 사용자 결정(REQ-002, ADR-007). 5.2 LTS는 2028년 4월까지 보안 지원. 참고로 6.1은 `django-celery-beat` 2.9.0(`Django <6.1`)이 막고 있다 | 2026-11-12 | 2028년 4월 지원 종료 전, 또는 사용자가 6.x를 요청할 때 |
| R-003 | 2019~2022년 이후 새 릴리스가 없는 패키지(django-summernote, django-user-agents, django-request-logging)가 새 Django에서 런타임 문제를 낼 수 있다 | MED | 교체는 비목표. 테스트·runserver로 확인한다 | 2026-11-12 | 동작 오류가 나면 ledger로 올리고 교체 여부를 묻는다 |
| R-004 | 테스트가 없는 화면(소셜 로그인 콜백, admin 일부, 이미지 썸네일 생성)은 runserver 점검표로만 확인된다 | MED | 테스트 확충은 이 단계의 목표가 아니다 | 2026-11-12 | 점검표에서 문제가 보이면 ledger로 |
