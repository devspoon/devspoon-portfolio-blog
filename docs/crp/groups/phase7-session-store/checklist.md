# Checklist — phase7-session-store

## Round 1 — 2026-11-14
- [x] 현재 세션 설정·TTL·생성 시점·Redis DB 사용 조사
- [x] 설계 v0.1(Redis DB 분리) 작성
- [x] 사용자 요청으로 v0.2(DB 저장) 재설계: DB 세션 읽기 경로·세션 테이블·주기 작업 방식 조사
- [x] D1~D4 모두 A, 설계 v0.2 승인
- [x] 계획 1~6 실행(테스트·fail-on-revert·전체 검증·dev 리허설·배포 문서)

## Round 2 — 2026-11-16 (전환 빈틈)
- [x] 빈틈 실측, 보고·`deploy.md` 오류 확인(F-004)
- [x] 설계 v0.3(ADR-007)·계획 작성
- [x] 설계 v0.3 승인
- [x] 계획 1~5 실행(테스트·fail-on-revert 4건·전체 검증·dev 리허설·deploy.md 정정)

## Round 3 — 2026-11-17 (전환용 엔진 제거)
- [x] 참조처 확인(설정 4곳, 테스트 묶음 1개)
- [x] 엔진·전용 테스트 삭제, 설정 복구
- [x] 전체 검증(750 passed / 1 skipped)·커밋
