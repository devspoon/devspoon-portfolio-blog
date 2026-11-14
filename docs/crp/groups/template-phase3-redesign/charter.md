# Charter — template-phase3-redesign  (Charter v0.1 / 2026-11-12)

> 상위 기준: `design-baseline.md`. 상세 작업은 `plan.md`.

## 1. 인벤토리 (현재 상태 — 조사 결과)
| 영역 | 경로 | 현재 | 목표 |
|---|---|---|---|
| CSS | `static/css/style.css`(74KB) | 클래스 386 중 사용 80(21%), 규칙 694 중 379개는 사용 클래스 없음 | 삭제 |
| CSS | `static/css/custom.css`(68KB) | 클래스 187 중 사용 140, `@media` 106 | 삭제(필요 규칙은 컴포넌트로 재작성) |
| CSS | `static/css/responsive.css` | **로드되지 않음** | 삭제 |
| 디자인 값 | 위 CSS | 글꼴 3, 글자 크기 38종, radius 17종, shadow 18종, `@media` 200 | 토큰: 글자 크기 7단계, radius 3, shadow 3, breakpoint = Bootstrap 5종 |
| 아이콘 | `static/vendors/icons/*` + CDN | Lineicons(8 파일)·Ionicons(3)·Icofont(1)·Flaticon(1)·FontAwesome(2+portfolio.js) | Bootstrap Icons 1종 |
| 애니메이션 | AOS(home·portfolio)·WOW(portfolio)·animate.css(home) | 3종 | 0(자체 1개 reveal + CSS transition) |
| 미사용 전역 로드 | tiny-slider·glightbox(주석 코드만)·Selectr·noUiSlider·Summernote CDN·axios(버전 미고정) | 매 페이지 로드 | 제거(Summernote는 django-summernote가 폼 iframe에서 자체 로드) |
| JS | `main.js`(103)·`blog.js`(42)·`blog_apis.js`(525)·`portfolio.js`(100) | 전역 함수, 문자열 HTML, 인라인 onclick 11파일 | ES 모듈 + `<template>` + 위임 |
| 컴포넌트 | 카드형 마크업 18 파일 | 홈·목록·포트폴리오가 서로 다른 카드 | `components/*.html` + `.c-*` CSS |
| 페이지네이션 | `pagenation.html`, `replies_pagination.html` | 2종 마크업·스타일 | 1종 |
| 이미지 | `static/images` 14MB(`test1.jpg` 1.6MB, `profile_img/Originals` 4MB) | 원본 크기 그대로 | 반응형 WebP·lazy·width/height, 미사용 파일 정리는 사용자 확인 |
| 템플릿 | 2단계 결과(공통 3 + 자식) | 구조 정리됨 | 컴포넌트 include로 전환 |

## 2. 계약
### 2-1. 지원 환경
- 브라우저: 최신 2개 버전의 Chrome·Edge·Safari·Firefox, iOS Safari 16+, Samsung Internet 최신. (`@layer`·`:focus-visible`·`aspect-ratio` 사용 가능 범위)
- 화면 폭: 360px ~ 1920px. JS 꺼짐에서도 읽기·이동 가능(점진적 향상)
### 2-2. 위협 모델 (1단계 계약 유지)
- 방어: 저장형 XSS(본문·댓글·JS 렌더링), CSRF, 권한 우회. 새 JS의 DOM 렌더링은 `textContent`/`<template>`만
- 비방어: 관리자 입력 `|safe`(포트폴리오·약관), CSP(이번 그룹에서 nonce 없는 CSP 준비까지만 — 선택)
### 2-3. 불변식
- INV-1: 색·글꼴·간격·반경·그림자 값은 `app.css`의 `@layer tokens`에만 존재(다른 CSS에서 hex·px 리터럴 금지 — 0, 1px 선·백분율 예외)
- INV-2: 같은 역할의 UI는 같은 컴포넌트 템플릿과 같은 클래스를 쓴다(카드 4변형은 `.c-card` 하나의 변형)
- INV-3: 페이지당 CSS ≤ 2파일(app + page), JS는 모듈 진입점 1개 + 페이지 모듈
- INV-4: 1단계 보안 테스트·2단계 특성화 테스트의 **기능** 단언 유지(마크업 단언은 새 계약으로 갱신)
- INV-5: WCAG 2.2 AA — axe 위반 0(critical·serious), 키보드로 모든 기능 사용 가능
### 2-4. 비목표
- Node 빌드 도구·Tailwind·React/shadcn 컴포넌트 도입(사용자 결정: Bootstrap·빌드 없음)
- 관리자(admin)·이메일 템플릿 리디자인
- 백엔드 기능 추가(검색 고도화, 새 페이지). Django 버전 업그레이드는 트랙 B(ADR-010)

## 3. 인수 기준
> 2026-11-13 측정 결과는 run-log Round 5.
- [ ] Lighthouse(모바일, 대표 6페이지): Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 95, SEO ≥ 95 — **A100·SEO100 통과, BP 93~100(R-007·R-011), P 70~79 / gzip 84~96 미달(R-013)** → Round 6 글꼴 CSS 비차단 후 gzip 조건 P 중앙값 97~99(운영 압축 확인 필요)
- [x] axe-core: critical·serious 위반 0 (전 페이지) — 22쪽 × 2테마 × 2폭, 모든 영향도 0
- [x] 전송량: 첫 화면 CSS+JS+폰트 합계가 현재 대비 50% 이상 감소(기준선 측정값 대비) — 2,379KB → 983~994KB(-59%)
- [x] INV-1 검사 스크립트: 토큰 파일 밖 색 리터럴 0
- [x] 미사용 CSS 클래스 비율 ≤ 5%(css_usage 스크립트) — 0.9%
- [x] pytest 전체 통과(WSL), djLint 구조 규칙 위반 0(새로 쓴 템플릿) — 156 passed·1 skipped, H025 1건 오탐(if 블록 안 짝 맞음)
- [ ] 다크/라이트 × 360·768·1366 폭 스크린샷 리뷰 세트 사용자 확인 — STOP ③
- [x] security-review 신규 취약점 0 (범위 밖 기존 키 노출은 R-014)
- [ ] 콘솔 오류 0(전 페이지, Playwright MCP) — 상세 2쪽 방문 집계 500 1건(테스트 환경 SQLite, R-011)

## 4. 변경 이력
- v0.1 (2026-11-12): 최초 작성.
