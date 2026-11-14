# Checklist — phase5a-integration

## Round 1 — 2026-11-13
- [x] 요청 기록(REQ-001)과 해결 원칙(ADR-001~006)
- [x] 그쪽 결정 학습
- [x] 병합, 충돌 18개 + 이름 충돌 1개 해결
- [x] 의미상 충돌 검사(옛 캐시 API 호출 0, 댓글 삭제 POST 전용)
- [x] 실행 중 발견 F-001~F-004 수정, F-005 테스트 갱신, F-006 결정 승계
- [x] 전체 테스트 545 passed / 1 skipped, check·migration 통과
- [x] runserver: 점검표·좋아요 동시 요청·정적 파일·주요 화면·SCAN 0
- [x] 판정 CONVERGED

## Round 2 — 2026-11-13
- [x] 댓글 JSON B안 결정 기록(REQ-002, ADR-007)
- [x] 그쪽 `37a296e`까지 병합, 충돌 8개 해결
- [x] `comments.js`·`comments.html`·그쪽 테스트를 B안으로(F-007)
- [x] 지워진 정적 파일 참조 검사
- [x] pytest 548 passed / 1 skipped, check·이쪽 앱 migration 통과
- [x] runserver: 점검표·`author_id` 비공개·정적 파일·좋아요 동시 요청·SCAN 0
- [x] 판정 CONVERGED

## Round 3 — 2026-11-14
- [x] 그쪽 `54976ab`까지 병합, 충돌 0
- [x] 전체 테스트·check·migration
