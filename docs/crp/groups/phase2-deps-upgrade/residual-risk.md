# Residual Risk — phase2-deps-upgrade (잔여 위험 등록부)

| ID | 항목 | Severity | 왜 비범위인가 | 수용일 | 재평가 조건 |
|---|---|---|---|---|---|
| R-001 | 운영 서버의 Python이 3.12 미만이면 배포 후 동작하지 않는다 | HIGH | 인프라는 고려하지 않는다(phase1 REQ-003). 배포 워크플로는 별도 저장소의 docker 구성을 쓴다 | 2026-11-12 | 서버 배포를 요청받으면 그 전에 서버 Python 버전을 확인한다 |
| R-002 | Django 6.x로 올리지 않고 5.2 LTS에 머문다 | LOW | 사용자 결정(REQ-002, ADR-007). 5.2 LTS는 2028년 4월까지 보안 지원. 참고로 6.1은 `django-celery-beat` 2.9.0(`Django <6.1`)이 막고 있다 | 2026-11-12 | 2028년 4월 지원 종료 전, 또는 사용자가 6.x를 요청할 때 |
| R-003 | 2019~2022년 이후 새 릴리스가 없는 패키지(django-summernote, django-user-agents, django-request-logging)가 새 Django에서 런타임 문제를 낼 수 있다 | MED | 교체는 비목표. 테스트·runserver로 확인한다 | 2026-11-12 | 동작 오류가 나면 ledger로 올리고 교체 여부를 묻는다 |
| R-004 | 테스트가 없는 화면(소셜 로그인 콜백, admin 일부, 이미지 썸네일 생성)은 runserver 점검표로만 확인된다 | MED | 테스트 확충은 이 단계의 목표가 아니다 | 2026-11-12 | 점검표에서 문제가 보이면 ledger로 |
| R-005 | allauth 65의 `account` migration 0006~0009는 운영 DB의 `account_emailaddress` 데이터를 바꾼다(이메일 소문자화, 사용자당 대표 이메일 1개로 정리 후 unique 제약) | MED | 서버 배포는 범위 밖(phase1 REQ-003). 로컬 dev DB에서는 문제없이 적용됨 | 2026-11-12 | 운영 반영 전 DB 백업 후 적용하고, 중복 대표 이메일이 있는지 미리 확인한다 |
| R-006 | Django 6.x로 올리면 `forms.URLField`가 scheme 없는 입력을 https로 해석한다(현재 http). 경고는 5.2에서 계속 나온다 | LOW | 사용자 결정 "http 유지"(REQ-003, ADR-009). 5.2에서는 동작 변화 없음 | 2026-11-12 | Django 6.x 업그레이드를 설계할 때 http/https를 정하고 모델 URLField 34개에 `assume_scheme`을 지정한다 |
| R-007 | sentry-sdk의 `send_default_pii`는 deprecated다. 이후 sentry-sdk 메이저에서 제거되면 설정이 동작하지 않을 수 있다 | LOW | 사용자 결정(REQ-003, ADR-010). 개인정보 범위 결정은 보류 | 2026-11-12 | sentry-sdk 메이저 업그레이드 때, 또는 Sentry 개인정보 정책을 정할 때 `data_collection`으로 옮긴다 |
