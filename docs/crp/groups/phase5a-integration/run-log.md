# Run Log — phase5a-integration (라운드 로그 + 수렴 판정)

### Round 1 — 2026-11-13 (이쪽 `f72d71a` + 그쪽 `287639c`, 브랜치 `crp/phase5a-integration`)
- **트리거:** 사용자 "권장안대로 A로 진행해줘"
- **학습:** 그쪽 그룹 3개(`template-phase1-security`·`template-phase2-structure`·`template-phase3-redesign`)의 REQ·ADR·C 읽음. 해결 원칙 ADR-001~006 기록
- **병합:** `git merge --no-ff --no-commit 287639c` → 내용 충돌 18개(사전 계산과 같음)
- **해결:** charter §1. 실행 중 발견·수정: F-001(이름 충돌), F-002(기술 스택 캐시 무효화 누락), F-003(새 검색 템플릿의 잘못된 책 링크), F-004(새 문의 폼에서 captcha·길이 제한 누락). 그쪽 결정 승계: F-006(홈 최신순)
- **검증 1차:** pytest 17 failed / 527 passed — 전부 그쪽 계약 변경을 이쪽 테스트가 따라가지 못한 것(F-005) → 요청 방식만 갱신
- **검증 최종:** check exit 0, `makemigrations --check` No changes, pytest **545 passed / 1 skipped**. runserver(PostgreSQL, 18765): 점검표 전부 통과(댓글 삭제·좋아요를 POST+CSRF로 갱신, 수정 버튼은 새 마크업 `detail-button-group` 기준 1/0/0), 좋아요 동시 10·11개 → 0/0·1/1 전부 200, 상세 화면 정적 파일 22개 전부 200, 검색·게시판·로그인·가입·경력 JSON 200, 고정 요청 16개에서 **SCAN 0 · TTL 0**
- **GATE 통과:** 0 ■ 1 ■ 2 ■ 3 ■ 4 ■ 5 ■
- **수렴 판정:** `CONVERGED` — Open Fix 0, 양쪽 계약 위반 0
- **검사 범위의 한계:** CI 미실행(push 안 함). 그쪽 이후 커밋 미포함(R-001). 스크린샷 비교 안 함(R-004)

## 작업 계획 (실행됨)
| 순서 | 단계 |
|---|---|
| 1 | 그쪽 결정 학습, 해결 원칙 기록 |
| 2 | 통합 브랜치에서 병합(커밋 없이) |
| 3 | 충돌 해결(뷰 → 모델 → 에러 → index·portfolio → 템플릿 → 의존성), 이름 충돌 처리 |
| 4 | 의미상 충돌 검사(옛 API 호출, POST 전용 병합 결과) |
| 5 | 전체 테스트, runserver·정적 파일·SCAN 확인 |
| 6 | 병합 커밋 |

## 심각도 추세
| Round | CRIT | HIGH | MED | LOW | 신규 Fix | 판정 |
|---|---|---|---|---|---|---|
| 1 | 0 | 1 | 3 | 1 | 5 Fixed(F-001~F-005), 1 Accepted(F-006) | CONVERGED |
