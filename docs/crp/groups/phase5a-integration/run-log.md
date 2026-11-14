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
| 2 | 0 | 0 | 1 | 0 | 1 Fixed(F-007) | CONVERGED |

### Round 2 — 2026-11-13 (통합 `ab26e10` + 그쪽 `37a296e`)
- **트리거:** 사용자 "권장 방법으로 진행해줘"(댓글 JSON B안)
- **병합:** `git merge --no-ff --no-commit 37a296e` → 충돌 8개(댓글 뷰, 사전 계산과 같음)
- **해결:** 뷰 8개 이쪽 유지. 그쪽 `comments.js` 판단 1줄을 `r.user_auth`로, `data-viewer` 제거, 그쪽 테스트 B안 뜻으로 갱신(F-007). 지워진 정적 파일 138개의 남은 참조 검사 → 주석·경로 문자열뿐, 낡은 주석 1곳 갱신
- **검증:** pytest **548 passed / 1 skipped**, check ERROR 0, 이쪽 앱 `makemigrations --check` No changes(전체 앱은 R-005). runserver(PostgreSQL, 18765): 점검표 전부 통과(`user_auth` true/false/false, 수정 버튼 1/0/0, 댓글 삭제 302), 실제 응답에 `author_id` 0·페이지에 `data-viewer` 0, 새 `app.css`·`comments.js` 200, 좋아요 동시 10개 → 0/0 전부 200, Redis 명령 GET·SET만(SCAN 0 · TTL 0)
- **수렴 판정:** `CONVERGED` — Open Fix 0
- **검사 범위의 한계:** CI 미실행. 브라우저에서 댓글 버튼을 직접 눌러 보지는 않음(서버 응답과 내려가는 JS로 확인)

### Round 3 — 2026-11-14 (5단계 브랜치 `crp/phase5-request-security` + 그쪽 `54976ab`)
- **트리거:** 사용자 "작업 재개해줘". 그쪽에 새 커밋 2개(`df41a88` 한국어 번역·편집기 iframe 제목·정책 페이지 h1, `54976ab` Pretendard CSS 비차단 로드)
- **판단:** `git merge-tree` 충돌 0. 변경은 폼 라벨 번역 처리·번역 파일·템플릿·테스트뿐이고 이쪽 5단계 변경(`comments.html` 포함)과 겹치지 않음. 사용자 동작이 다르게 결정된 곳이 없어 ADR-006(질문) 대상 아님 → ADR-001~005대로 병합
- **병합:** 5단계 브랜치에 직접(통합 브랜치는 5단계 브랜치의 조상이라 같은 줄기)
