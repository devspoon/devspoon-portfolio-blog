# Residual Risk — template-phase2-structure

| ID | 항목 | Severity | 왜 비범위인가 | 수용일 | 재평가 조건 |
|---|---|---|---|---|---|
| R-001 | djLint 남은 8건: header `</div>` 1개 초과, profile/register/portfolio div 불균형·onclick 중복, index·forgot 상대 링크 | LOW | 모두 기존 결함. 브라우저 자동 보정 위치를 바꾸면 레이아웃이 바뀔 수 있어 CSS와 함께 정리 | 2026-11-11 | 3단계(CSS) 착수 시 |
| R-002 | 폼 머리말 `<h4>`(페이지 `<h1>` 없음), 메타 값 `<a href="#">`, 비밀번호 교체 `<a><button>` | LOW | 테마 CSS가 태그 기준 → 마크업만 바꾸면 모양 변경(C-2) | 2026-11-11 | 3단계 |
| R-003 | 목록·검색 제목 문구가 URL 조각(`ONLINESTUDY`, `QUERYSET`) | LOW | 화면 유지(C-2). 문구 개선은 디자인 단계 | 2026-11-11 | 5단계 |
| R-004 | 홈·검색 화면은 픽셀 비교 제외 | LOW | 화면용 SQLite가 UNION+LIMIT 쿼리 미지원. 홈 변경은 alt 1개, 검색은 제목 서버 렌더링(테스트·HTML 확인) | 2026-11-11 | MySQL 화면 환경이 생기면 |
| R-005 | 화면용 환경에서 댓글·조회수 API가 간헐 500(SQLite 동시 쓰기) | LOW | 운영 DB(MySQL)와 다름. 촬영 스크립트는 재시도 | 2026-11-11 | 운영 로그에서 같은 증상 확인 시 |
