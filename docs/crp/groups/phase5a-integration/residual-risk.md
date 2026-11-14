# Residual Risk — phase5a-integration (잔여 위험 등록부)

| ID | 항목 | Severity | 왜 비범위인가 | 수용일 | 재평가 조건 |
|---|---|---|---|---|---|
| R-001 | 그쪽 브랜치는 `54976ab`(Round 3)로 고정해 합쳤다. 그쪽 세션이 이후 커밋을 더 쌓았으면 다시 합쳐야 하고, 그쪽은 이쪽 변경(캐시 v2·mixin·좋아요 제약·Django 5.2)을 모른 채 작업 중일 수 있다 | MED | 그쪽 세션 진행 여부를 확인하지 못함 | 2026-11-13 | 그쪽에 새 커밋이 생기면 이 통합 브랜치에 다시 병합. 그쪽 세션이 앞으로 이 통합 브랜치 위에서 작업하도록 안내하는 것을 권함 |
| R-002 | 그쪽 ADR-007은 Windows에서 `nh3` DLL이 앱 제어 정책에 막힌다고 기록했다. 이 환경(Windows `.venv`, nh3 0.3.7)에서는 import·정화가 동작했다 | LOW | 환경 차이(버전·정책) | 2026-11-13 | 다른 Windows 환경에서 import 오류가 나면 WSL 테스트로 |
| R-003 | 그쪽 문서(`docs/crp/groups/template-*`)의 일부 서술은 통합 전 코드 기준이다(예: `apply_viewer_state`, `common/mixin/views.py`) | LOW | 그쪽 그룹 문서는 고치지 않는다(C-2 취지) | 2026-11-13 | 그쪽 그룹을 이어서 작업할 때 이 ledger를 참고 |
| R-004 | 시각 확인은 정적 파일 응답(22개 200)과 화면 응답 코드·마크업 기준으로만 했다. 스크린샷 비교는 하지 않았다 | LOW | 그쪽은 Playwright로 시각 검증을 했고 이쪽 변경은 마크업 두 곳뿐 | 2026-11-13 | 화면 이상이 보고되면 |
| R-005 | `makemigrations --check`를 전체 앱으로 돌리면 외부 패키지 `django_summernote`의 빠진 마이그레이션(`attachment` `file`·`id`)이 나온다. 이쪽 앱만 대상으로 하면 No changes | LOW | 외부 패키지 문제이고 이쪽 앱 스키마와 무관. 서버는 마이그레이션을 생성하는 방식이라 배포 때 `makemigrations`가 패키지 폴더에 파일을 만들 수 있다 | 2026-11-13 | 6단계 정리 때 `DEFAULT_AUTO_FIELD`·summernote 버전을 함께 검토 |
