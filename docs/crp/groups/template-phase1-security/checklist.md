# Checklist — template-phase1-security

## Round 1 — 2026-11-11
- [x] 이번 요청을 design-baseline §2에 기록 + 이전 요구 충돌 확인
- [x] (F-001) 댓글 escapeHtml — node assert
- [x] (F-002) 본문 sanitize_html — 필터 단위 + 상세 8종 렌더 테스트
- [x] (F-003·004·005) GET=405 / POST 동작 — 파라미터화 테스트
- [x] (F-006) staff 작성 제한 — 일반 회원 403, 비로그인 → 로그인 페이지
- [x] (F-007~F-011) 발견된 기존 버그 — 각 회귀 테스트
- [x] GATE 3 인수기준 전부 그린(98 passed)
- [x] 요구사항 회귀 0 — C-2(기존 동작), C-3(JSON 형식 불변), C-4(Summernote 서식 유지) 확인
- [x] run-log 갱신 + 수렴 판정
- [x] residual-risk 갱신
- [ ] 브라우저 실화면 확인(삭제 버튼·댓글·좋아요) — 개발 서버 미기동, 사용자 확인 필요
