# AI Docs Index

이 폴더는 `docs/error`의 Sentry 이슈를 Codex와 Claude가 함께 검토하고 후속 구현을 진행하기 위한 작업 문서 모음이다.

## 진행 상태

2026-08-10 기준 Phase 1~5 구현이 완료됐고 테스트는 115 passed / 1 skipped다.
Phase 0(nginx)과 SendGrid 계정 점검은 운영 작업으로 남아 있다.
구현 내용과 배포 절차는 [reports/06-implementation-report.md](reports/06-implementation-report.md)를 본다.

## 문서 구조

- [reports/00-total-report.md](reports/00-total-report.md): 전체 요약, 우선순위, 승인/검토 포인트
- [reviews/01-sentry-error-review.md](reviews/01-sentry-error-review.md): Sentry 이슈별 원인 검수
- [security/02-nginx-php-scan-blocking.md](security/02-nginx-php-scan-blocking.md): PHP/WordPress 스캔 트래픽 nginx 1차 차단 방안
- [security/03-app-layer-access-guard-design.md](security/03-app-layer-access-guard-design.md): Django 애플리케이션 2차 접근 차단 설계
- [plans/04-remediation-work-plan.md](plans/04-remediation-work-plan.md): 구현 작업 계획서
- [handoff/05-agent-handoff.md](handoff/05-agent-handoff.md): Codex/Claude 공용 핸드오프 체크리스트
- [reports/06-implementation-report.md](reports/06-implementation-report.md): 구현 결과, 검증 기록, 운영 배포 절차

## 기준 자료

- `docs/error/DataError.md`
- `docs/error/ConnectionHardwareStats.MultipleObjectsReturned.md`
- `docs/error/ConnectionMethodStats.MultipleObjectsReturned.md`
- `docs/error/Error sending email to ['[email]']: HTTP Error 401: Unauthorized.md`
- `docs/error/Failed to send email, error: HTTP Error 401: Unauthorized, response body: b'{"errors":[{"message":"Maximum credits exceeded","field":null,"help":null}]}'.md`

## 검토 기준

- nginx에서 명확한 비서비스 트래픽은 애플리케이션 도달 전에 차단한다.
- Django에서는 nginx 누락, 내부 우회, 설정 실수에 대비해 조기 반환 방어선을 둔다.
- Sentry에 기록된 런타임 예외는 입력 검증, DB 제약, 데이터 정리, 외부 서비스 상태를 분리해 해결한다.
- 구현자는 이 문서를 기준으로 코드 변경 전 데이터 백업/마이그레이션 영향도를 재확인한다.
