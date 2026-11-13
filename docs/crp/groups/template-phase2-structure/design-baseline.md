# Design Baseline — template-phase2-structure (템플릿 고도화 2단계: HTML 구조 개선·템플릿 통합)

> append-only. 상위 맥락: `../template-phase1-security/` (1단계, 커밋 2db0de7)

## 0. 질의 수준
- [x] **적극(Thorough)** · 선택일: 2026-11-11

## 1. 목적 / 배경
템플릿 61개 중 블로그 5종·게시판 3종의 상세·작성·수정 템플릿이 복사본으로 존재하고(차이는 제목·메타 블록뿐),
목록 제목·링크를 JS가 URL을 잘라 다시 쓰며, 태그 짝 불일치·중첩 대화형 요소·중복 `<title>` 등 구조 결함이 있다.
**화면 모양은 바꾸지 않고**(CSS는 3단계, 디자인은 5단계) 마크업 구조·중복·서버 렌더링 정확성만 바로잡는다.

## 2. 요구사항 레지스터
| Req-ID | 날짜 | 요청(원문 요약) | 도출된 요구사항 | 상태 | 연결 |
|---|---|---|---|---|---|
| REQ-001 | 2026-11-11 | (1단계 REQ-001) 템플릿 구조 개선·중복 통합 | 2단계 = HTML 구조·템플릿 통합 | Active | ADR-001~007 |
| REQ-002 | 2026-11-11 | 모든 작업은 설계·작업 계획 승인 후 실행, 계획 밖 수정은 먼저 질문 | 승인 STOP + 실행 중 이탈 시 STOP | Active | C-1 |
| REQ-003 | 2026-11-11 | "승인한다" — 2단계 설계·작업 계획 작성 | 이 문서 | Active | — |

## 3. 설계 결정 (ADR)
| ADR-ID | 결정 | 근거 | 상태 |
|---|---|---|---|
| ADR-001 | **상세 통합**: `blog/_post_detail.html`(공통) + 5종 자식(제목·`{% block post_meta %}`만), `board/_board_detail.html` + 3종 자식. 뷰의 `template_name`은 그대로 | 5종 차이 = 제목+메타 블록(diff 확인). 자식 템플릿 방식이면 Python 변경 0 | Accepted |
| ADR-002 | **폼 통합**: 작성·수정 16개 → `base/post_form.html` + 16개 자식(제목·머리말·취소 URL 블록). 필드 렌더링 방식(수동 `<input>`)은 유지 | 16개가 제목·머리말·들여쓰기만 다름. 렌더링 방식 변경은 모양이 바뀌므로 3·5단계 | Accepted |
| ADR-003 | **목록**: 8개 ListView에 `extra_context`(page_title, detail/create URL 이름) 추가 → 제목·breadcrumb·링크를 서버가 렌더링. `blog.js`의 URL 기반 제목·링크 재작성 코드 삭제 | 현재 `<title>`이 "title", 본문 제목이 JS 의존(검색엔진·JS 꺼짐에서 깨짐) | Accepted |
| ADR-004 | **이전·다음 글 링크**: `{% url ... pre_board.pk %}`로 생성, `blog.js` ±1 계산 삭제 | books 계열은 `pre_board.id`에 다시 -1 → 잘못된 글로 이동(버그) | Accepted |
| ADR-005 | **레이아웃**: `base.html`에 `<main>` 추가, `meta.html`의 중복 `<title>` 삭제, header 태그 짝·mobile_menu 중복 속성·pagination 중첩 링크·버튼 type·img alt 수정 | djLint H025/H037/H054/H043/H013 | Accepted |
| ADR-006 | **시맨틱**: 상세는 `<article>`, 날짜는 `<time datetime>`, 페이지당 `<h1>` 하나. 모양 유지를 위해 기존 class 유지(`<h1 class="title">` 등 — 필요 시 `h2` 크기 class 부여) | 접근성·SEO. 시각 회귀 없음이 원칙(C-2) | Accepted |
| ADR-007 | **명백한 텍스트 버그 수정**: 수정 폼 머리말 "OpenSource" 복붙 오류, 취소 링크가 로그인 페이지로 가는 문제, "Cancle" 오타 | 사용자에게 보이는 결함. 문구 자체 개편은 비범위 | Accepted |
| ADR-008 | 브랜치: 1단계 커밋 2db0de7 위에 `template-phase2-structure` | 사용자 확정. 1단계를 먼저 병합해야 함 | Accepted |
| ADR-009 | 시각 검증: WSL 개발 서버(별도 SQLite·샘플 데이터, `runserver --insecure`) + Chrome 스크린샷 변경 전·후 비교 | 사용자 확정 | Accepted |
| ADR-011 | ADR-009 보완: Chrome 확장 미연결로 스크린샷은 WSL Playwright(헤드리스 Chromium) 전체 페이지 PNG + 픽셀 diff. 추가로 렌더링 HTML 기준선(비로그인·staff 104개) diff. 홈·검색은 SQLite가 UNION 쿼리를 못 돌려 화면 비교 제외(테스트로 검증) | 사용자 확정(2026-11-11) | Accepted |
| ADR-012 | 실행 중 결정(계약 축소): 폼 페이지 머리말은 `<h4>` 유지(테마가 `h4`·`.box .box-body h4`를 태그로 스타일링 → `<h1>`이면 모양 변경). 목록 제목·탭 제목은 JS가 넣던 URL 조각(`project`, `onlinestudy` 등)을 서버가 그대로 출력. 메타 값 `<a href="#">`·비밀번호 교체의 `<a><button>`은 CSS 필요로 유지 | C-2(시각 회귀 없음)가 INV-2보다 우선. 문구·태그 개선은 3·5단계 | Accepted(사용자 사후 확인 필요) |
| ADR-013 | djLint는 1.36.x로 고정 | 1.49.x는 `click` 8.1.8→8.5.1 업그레이드를 끌어옴(Celery 사용). 1.36.4는 기존 lock 패키지 버전 변경 없음 | Accepted |
| ADR-010 | djLint: poetry dev 그룹 + pyproject `[tool.djlint]`(구조 규칙 중심). 일괄 포맷·CI 추가 없음 | 사용자 확정 | Accepted |

## 4. 불가침 제약
- C-1: 승인 전 코드 편집 금지, 실행 중 계획 이탈은 수정 전 질문 (REQ-002)
- C-2: **시각 회귀 없음** — 기존 class·레이아웃 유지(디자인 변경은 3·5단계)
- C-3: 1단계 보안 계약 유지 — 삭제 POST 폼·`sanitize_html`·escapeHtml·staff 작성 제한(1단계 INV-1~3)
- C-4: 뷰 동작·URL·폼 필드·JSON API 불변 (ListView `extra_context` 추가만 허용)

## 5. 변경 이력
- v0.1 (2026-11-11): 최초 작성(조사 결과 + 설계안).
