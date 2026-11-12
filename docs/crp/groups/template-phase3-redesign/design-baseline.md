# Design Baseline — template-phase3-redesign (디자인 시스템 재구축: CSS·JS 통합 + 현대적 리디자인)

> append-only. 선행: `../template-phase1-security/`(2db0de7), `../template-phase2-structure/`(9b24050)

## 0. 질의 수준
- [x] **적극(Thorough)** · 선택일: 2026-11-12

## 1. 목적 / 배경
devspoon은 한 개발자의 **포트폴리오 + 기술 블로그(5종) + 게시판(공지·방명록·재활성화)** 사이트다.
현재 화면은 GrayGrids "ClassiList" 템플릿 위에 덧칠한 CSS(사용률 21%), 5종 아이콘 폰트, 3종 애니메이션 라이브러리,
쓰지 않는 전역 라이브러리로 이루어져 있다. 카드·목록·폼·페이지네이션이 페이지마다 다른 CSS를 쓴다.
이 그룹은 **하나의 디자인 시스템(토큰 + 컴포넌트)으로 모든 페이지를 다시 짓고**, CSS·JS를 정리·최신화한다.
화면 유지는 요구사항이 아니다(사용자 2026-11-12). 2단계에서 만든 템플릿 구조·테스트 위에서 진행한다.

## 2. 요구사항 레지스터
| Req-ID | 날짜 | 요청(원문 요약) | 도출된 요구사항 | 상태 | 연결 |
|---|---|---|---|---|---|
| REQ-001 | 2026-11-12 | 설치한 디자인 플러그인·스킬·MCP 기반으로 고도화·리팩토링 기획·설계·작업계획 정리 | 이 그룹 문서(design-baseline·charter·plan) | Active | — |
| REQ-002 | 2026-11-12 | CSS·JS 최적화·정리, 통일성. 카드 섹션 등 여러 디자인이 동일한 CSS 설정 | 토큰 + 단일 컴포넌트 CSS + 공통 컴포넌트 템플릿(include) | Active | ADR-003~006 |
| REQ-003 | 2026-11-12 | 화면 유지 불필요, 세련된 최신 현대적 디자인 | 새 시각 방향(시안 비교 후 확정) | Active | ADR-002 |
| REQ-004 | 2026-11-12 | 버전 최신화 허용 | 프론트 라이브러리 최신 안정판, 백엔드(Django) 버전은 별도 트랙 결정 | Active | ADR-001, ADR-010 |
| REQ-005 | 2026-11-12 | 필요한 것 최대한 모두 고려 | 접근성·성능·SEO·다크모드·i18n·보안·테스트·운영 포함 | Active | charter §2 |
| (상속) | 2026-11-11 | 모든 작업은 설계·계획 승인 후, 실행 중 계획 이탈은 수정 전 질문 | STOP 규약 | Active | C-1 |

## 3. 설계 결정 (ADR)
| ADR-ID | 결정 | 근거 | 상태 |
|---|---|---|---|
| ADR-001 | **Bootstrap 5.3.8 유지·업그레이드**(5.1.3→5.3.8). 6.0은 알파라 제외. 빌드 없음(사용자 결정 유지) | 5.3은 CSS 변수 기반 테마·`data-bs-theme` 다크모드 제공 → 토큰 체계와 직결. 6.0 alpha는 운영 부적합 | Accepted |
| ADR-002 | **디자인 방향은 시안 2안 비교 후 확정**(plan.md §2 초안). frontend-design 지침의 "흔한 기본값" 회피 검토를 시안 단계에 포함 | 화면 유지 불필요 → 방향 선택이 가장 큰 결정. 승인 STOP | Accepted |
| ADR-003 | **토큰 계층**: `app.css`의 `@layer tokens`(원시값: 색·글꼴·간격·반경·그림자·모션) → Bootstrap CSS 변수(`--bs-*`) 재정의 → 컴포넌트는 토큰만 참조. 하드코딩 색 0 | 카드·목록 등이 같은 값을 쓰는 단일 출처 | Accepted |
| ADR-004 | **CSS 구조**: `@layer reset, vendor, tokens, base, components, pages, utilities`. 파일 = `app.css`(tokens·base·components, 모든 페이지) + `pages/<page>.css`(해당 페이지만 `{% block extra_css %}`). 기존 `style.css`·`custom.css`·`responsive.css` 삭제 | 캐스케이드 층으로 특정도 싸움 제거, 빌드 없이 파일 2개 이하/페이지 | Accepted |
| ADR-005 | **컴포넌트 단일화**: 카드(post·project·topic·timeline 4변형, 같은 `.c-card` 기반), 섹션 헤더, 버튼, 폼, 목록/테이블, 페이지네이션(현재 2종→1종), 댓글, 태그, 메타, 빈 상태, 알림. Django `{% include "components/…" %}`로 마크업도 한 곳 | REQ-002의 핵심 — 같은 모양 = 같은 템플릿 + 같은 CSS | Accepted |
| ADR-006 | **아이콘 1종**: Bootstrap Icons 1.13.1(SVG sprite, 사용 아이콘만). Lineicons·Ionicons(web component)·Icofont·Flaticon·FontAwesome 제거 | 5종→1종, 수 MB 감소, 웹컴포넌트 JS 제거 | Accepted |
| ADR-007 | **글꼴**: Pretendard Variable 1.3.9(한·영, dynamic subset, self-host) + 코드 블록 전용 고정폭 1종. Roboto·Poppins·Maven Pro 제거 | 한국어 본문 가독성, 3종 혼용 정리 | Accepted |
| ADR-008 | **JS 재작성**: ES 모듈(`type="module"`), jQuery·axios·AOS·WOW·animate.css·ionicons·glightbox·selectr·noUiSlider·tiny-slider·전역 Summernote 제거. `fetch` + CSRF 헬퍼, `<template>` 렌더링, 이벤트 위임, 페이지별 로드 | 사용처 0이거나 대체 가능(조사 결과). 인라인 onclick 제거 | Accepted |
| ADR-009 | **모션 원칙**: 페이지 진입 연출은 홈 1곳만, 나머지는 사용자 동작 응답(열기·좋아요·복사)만. `prefers-reduced-motion` 준수 | frontend-design 지침, AOS/WOW 제거 대체 | Accepted |
| ADR-010 | **Django 4.2(EOL 2026-04) → 5.2 LTS**는 별도 그룹·브랜치(트랙 B)로 설계·계획 승인 후 진행 | 보안 패치 종료 상태. allauth 0.58→65.x 등 파급 큼 → 디자인 작업과 섞지 않음 | Accepted |
| ADR-011 | **다크 모드**: `data-bs-theme` + 토큰 이중 정의, 시스템 설정 따름 + 토글(localStorage) | 5.3 기본 기능, 개발자 블로그 독자 기대 | Accepted |
| ADR-012 | **검증 도구**: 테스트=pytest(WSL), 상호작용=Playwright MCP, 시각 리뷰=WSL Playwright 전체 화면 촬영(전·후 비교는 회귀가 아닌 리뷰 자료), 접근성=axe-core + chrome-devtools a11y, 성능=Lighthouse(chrome-devtools MCP 또는 WSL), 템플릿=djLint, 보안=security-review | 설치된 MCP·스킬 활용 | Accepted |
| ADR-013 | impeccable 엔진(detect 등) 실행 허용 — WSL(Linux 바이너리, sha256 검증)에서 실행. 편집 훅(`hooks on`) 등록은 별도 승인 | 사용자 결정 2026-11-12 | Accepted |
| ADR-014 | shadcn(React+Tailwind) 미사용 — 잘못 설치된 파일 삭제 완료 | 사용자 결정, C-4·비목표와 일치 | Accepted |

## 4. 불가침 제약
- C-1: 승인 전 코드 편집 금지, 실행 중 계획 이탈은 수정 전 질문, push는 사용자만
- C-2: 1단계 보안 계약 유지 — POST 전용 상태 변경, `sanitize_html`, 댓글 escape, staff 작성 제한, CSRF
- C-3: URL·뷰 동작·폼 필드·JSON API 불변(마크업·스타일·클라이언트 JS만 변경). 예외는 ADR로 기록
- C-4: 빌드 도구 없음(Node 번들러 미도입). 정적 파일은 Django staticfiles로 서빙
- C-5: 접근성 하한 WCAG 2.2 AA(대비·키보드·포커스·대체 텍스트·모션 감소)

## 5. 변경 이력
- v0.1 (2026-11-12): 최초 작성 — 조사 결과와 설계안.
- v0.2 (2026-11-12): 계획 승인, ADR-010·013·014 결정 반영.
