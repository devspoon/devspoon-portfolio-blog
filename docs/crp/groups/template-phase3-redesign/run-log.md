# Run Log — <그룹 이름> (라운드 로그 + 수렴 판정)

> 각 라운드가 무엇을 검사했고 심각도 추세가 어떻게 변했는지. **수렴 추세가 한눈에 보여야** 한다.
> 마지막 라운드가 `CONVERGED` 이고 이후 코드·계약이 안 바뀌었으면 동일 요청은 "할 일 없음".

## 라운드 기록

### Round N — YYYY-MM-DD (base SHA: `_______`)
- **트리거:** (사용자 요청 / 코드 변경 / 계약 변경)
- **검수 범위:** (전수 / diff `A..B` / GATE3 실패분 / 신규 인벤토리)
- **GATE 통과:** 0 □ 1 □ 2 □ 3 □ 4 □ 5 □
- **신규 finding(심각도별):** CRIT 0 · HIGH 0 · MED 0 · LOW 0
- **신규 Fix(계약 위반):** __ 건 → ledger F-___ ~
- **수렴 판정:** `NOT CONVERGED` / `CONVERGED` (Fix 0건 + 인수기준 전부 통과 시 CONVERGED)
- **잔여 위험 변화:** (residual-risk 에 추가/승격된 항목)
- **깊이 주석(있으면):** (이번에 *처음 그 깊이로* 본 미감사 경로 — churn 아님을 명시)

### Round 1 — 2026-11-12 (base SHA: `527be3a`) — 3·4a 컴포넌트·파일럿
- **트리거:** 승인된 계획 3단계·4a
- **검수 범위:** 홈, 블로그 목록(5종 공용), 블로그 상세(5종 공용) / 컴포넌트 9개
- **검증:** pytest 148 passed·1 skipped(WSL) / 스크린샷 30장(3폭×2테마×5화면, JS 오류 0) /
  Lighthouse 모바일 — 홈 A96→브랜드 대비 수정, 목록 A100·BP100·SEO100, 상세 A90·BP100·SEO83(남은 것 R-002·R-003)
- **수정(자체 발견):** `<a class="btn">` 글자색 소실(vendor 층 < base `a`), `{# #}` 여러 줄 주석 노출(2단계 버그),
  레거시 `p{color}` 누수 → base `p{color:inherit}`, 푸터 브랜드 대비 2.94
- **계획 순서 조정:** form_field·auth_layout은 4b, comments는 5단계(사용처와 함께 검증)
- **수렴 판정:** `NOT CONVERGED` (STOP ② 사용자 리뷰 대기)
- **잔여 위험 변화:** R-001~R-006 추가

### Round 2 — 2026-11-13 (base SHA: `8649f7b`) — STOP ② 후속 + 4b 전체 적용
- **트리거:** STOP ② 사용자 결정 "권장 방식으로 진행" + 라이트 테마 푸터 흰색 + 주석 노출 보고
- **STOP ② 결정:** 파일럿 승인 / 홈 최신순(R-001 해소) / sanitize `alt=""` 기본(R-003 해소)
- **주석 노출 원인:** 8649f7b에서 `{% comment %}`로 고쳤으나 스크린샷 서버(`--noreload`, 템플릿 캐시)를 재시작하지 않아
  옛 출력이 남음 → 재시작 후 4페이지 0건 확인. 이후 템플릿 수정 뒤에는 서버 재시작 후 촬영
- **4b 범위:** 게시판 3종 목록·상세, 검색, 글 폼, 오류, 약관 2, 인증 6 + 프로필, 포트폴리오(스택 연결도·서버 렌더링 타임라인)
- **순서 조정:** 포트폴리오 타임라인을 5단계 대신 지금 서버 렌더링으로 전환(portfolio.js 삭제) — 레거시 JS 출력 재스타일보다 단순
- **삭제(미사용 확인):** base/pagenation.html, users/forgot.html, static/js/portfolio.js
- **검증:** pytest 152 passed·1 skipped / 스크린샷(그룹별 3폭×2테마) / Lighthouse 모바일 포트폴리오 100·100·100, 로그인 100·96·100
- **수렴 판정:** `NOT CONVERGED` (5단계 JS 재작성 남음)
- **잔여 위험 변화:** R-001·R-003 해소, R-007~R-009 추가

### Round 3 — 2026-11-13 (base SHA: `287639c`) — 5단계 JS 재작성
- **트리거:** 사용자 "작업을 재개해줘" → 승인된 계획 5단계
- **범위:** 댓글(components/comments.html + js/modules/comments.js), 좋아요·방문 집계(js/modules/post.js).
  작성·삭제는 일반 폼 POST(뷰가 리다이렉트), 수정·페이지만 fetch. DOM은 `<template>` 복제 + textContent(C-2)
- **형제 버그(ADR-017 계열):** 댓글 목록 JSON의 `user_auth`가 첫 요청자 기준으로 페이지 캐시에 저장되고,
  작성자 닉네임과 보는 사람 username을 비교해 틀린 값 → `author_id`로 바꾸고 판정은 페이지의 viewer id로(8개 뷰) + 회귀 테스트 3종.
  같은 파일의 `page` 기본값 정수 → 캐시 키 TypeError(페이지 없이 요청 시 500)도 `"1"`로 수정
- **삭제:** blog.js, blog_apis.js, base/javascripts.html, reply.html, replies_pagination.html, base의 legacy_js 블록. axios CDN 로드 제거
- **검증:** pytest 154 passed·1 skipped / Playwright 상호작용 7종(작성·답글 중첩·수정 저장·마크업 문자 표시·좋아요·익명 권한·페이지·삭제) 통과 /
  Lighthouse 모바일 상세 A100·BP96·SEO100(BP 감점은 R-011 테스트 환경 콘솔 오류)
- **다음:** 레거시 CSS를 쓰는 페이지 0개 → 6단계에서 legacy.css·style.css·custom.css·responsive.css 삭제 가능. 이미지 삭제는 사용자 확인 후
- **잔여 위험 변화:** R-002·R-006 해소, R-010·R-011 추가

### Round 4 — 2026-11-13 (base SHA: `61776e9`) — 6단계 정리(CSS·옛 vendor)
- **삭제(참조 0건 확인):** css/legacy.css·style.css(+map)·custom.css·responsive.css, static/vendors/(13MB: animate·bootstrap 구버전·icons·litebox·nouislider·selectr·slider), js/main.js,
  base의 legacy_css 블록과 페이지별 빈 오버라이드, app.css의 `legacy` 층과 이를 누르던 `p{color:inherit}`
- **이미지(2026-11-13 사용자 지시 "db와 모든 부분을 확인하여 사용하지 않는 이미지는 삭제"):** 54개 삭제(14MB → 48KB).
  근거: ① 추적 파일 724개 전체(문서·테스트·로케일 포함) 파일명 참조 0건(charter의 크기 기록 1건은 사용 아님)
  ② git 전체 기록에서 `profile_img` 참조 코드 없음(19e5061 "test AI images") ③ 로컬 PostgreSQL(127.0.0.1:25432/devspoon, READ ONLY)
  텍스트 컬럼 240개에서 참조 0건, `static/images/` 경로 언급 0건. 첫 목록에서 `2.png`가 `favicon-32x32.png` 부분 일치로 잘못 제외돼 추가 삭제.
  남은 5개: 소셜 로그인 버튼 3, 파비콘, logo.png(og/twitter 이미지). 삭제 파일은 git 기록에서 복구 가능
- **검증:** pytest 154 passed·1 skipped / 8개 페이지 응답 정상, legacy.css·axios·blog_apis 로드 0건

## 심각도 추세 (수렴이 보이게)
| Round | CRIT | HIGH | MED | LOW | 신규 Fix | 판정 |
|---|---|---|---|---|---|---|
| 1 |  |  |  |  |  |  |
