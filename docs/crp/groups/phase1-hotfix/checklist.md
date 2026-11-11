# Checklist — phase1-hotfix (개선 항목 추적판)

## Round 0 — 2026-11-11 (설계)
- [x] 이번 요청을 design-baseline §2에 기록(REQ-001) + 이전 요구 충돌 확인(없음)
- [x] 결함 목록 원장 등록(F-001~F-007), 형제 버그 전수 검색(blog·board 모두)
- [x] 계약·불변식·인수 기준 작성(charter v0.1)
- [x] **사용자 설계 승인**(ADR-001~005 Accepted, 2026-11-11)

## Round 1 — (sentry 브랜치 main 병합 후)
- [ ] 선행: 브랜치를 sentry 브랜치가 병합된 main 위로 rebase
- [ ] (F-004·F-005) 댓글 삭제 시그널 — 회귀 테스트, fail-on-revert
- [ ] (F-001·F-002) 상세 뷰 요청자별 값 — 회귀 테스트, fail-on-revert, Redis 키 검사
- [ ] (F-003·F-006) 댓글 목록 `user_auth`·N+1 — 회귀 테스트, fail-on-revert
- [ ] (F-007) `isort` import 제거
- [ ] GATE 3 인수 기준 전부 그린(CI 실제 실행)
- [ ] 요구사항 회귀 0 — 불가침 제약 C-1~C-6 위반 없음
- [ ] run-log 심각도 추세 갱신 + 수렴 판정
- [ ] residual-risk 갱신
