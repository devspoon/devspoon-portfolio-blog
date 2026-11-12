# Checklist — phase3-cache-redesign (개선 항목 추적판)

## Round 0 — 2026-11-12 (설계)
- [x] 이번 요청을 design-baseline §2에 기록(REQ-001) + 이전 요구 충돌 확인(phase1·phase2 불가침 제약 승계)
- [x] 캐시 사용처 전수 학습, django-redis 7 API 확인
- [x] 결함 F-001~F-010 등록, F-006 재현 확인
- [x] 계약·불변식·인수 기준 작성(charter v0.1)
- [x] 사용자 결정: D1-A(누구에게나 404), D2-A(상세 캐시 제거) — REQ-002
- [x] **사용자 설계 승인**(ADR-001~008 Accepted, 2026-11-12)

## Round 1 — 2026-11-12 (승인 후 실행)
- [x] 0 기준선
- [x] 1 보호 테스트
- [x] 2 캐시 모듈 + 무효화
- [x] 3 댓글 목록
- [x] 4 상세
- [x] 5 index·portfolio·메뉴
- [x] 6 정리
- [x] 7 마무리
- [x] 판정 NOT CONVERGED — 이번 범위 F-001~F-010 Fixed·불변식 통과, 실행 중 발견한 F-011·F-012 결정 대기

## Round 2 — 2026-11-12 (REQ-003)
- [x] F-012 게시판 삭제 — 실패 테스트 후 수정, 형제 버그 grep 3곳뿐
- [x] F-011 index — 실패 테스트 후 수정, PostgreSQL 결과 동일
- [x] 전체 검증 360 passed / 1 skipped, check·migration 통과
- [x] 판정 CONVERGED
