# Checklist — template-phase2-structure

## Round 1 — 2026-11-11
- [x] 요청을 design-baseline §2에 기록, 설계·계획 승인(STOP) 후 실행
- [x] 변경 전 기준선: 렌더링 HTML 104 + 스크린샷 48 + 잡음 측정
- [x] 특성화·계약 테스트 먼저 작성(24 green / 21 red)
- [x] (F-001~F-007) 상세·폼·목록 통합, 레이아웃 결함 수정
- [x] (F-008, F-009) 실행 중 시각 회귀 수정 + 회귀 테스트
- [x] djLint 도입(1.36.4, click 미변경)
- [x] 전체 테스트 그린(WSL)
- [x] 시각 비교 차이 전부 원인 규명
- [x] security-review — 신규 고신뢰 취약점 0 (sanitize_html·POST 삭제·csrf 유지, view_name 기반 URL은 요청으로 조작 불가)
- [x] run-log·residual-risk 갱신
- [ ] 사용자 확인: ADR-012(폼 h4 유지 등), 계획 밖 기존 결함 X-001~X-006 처리 여부
