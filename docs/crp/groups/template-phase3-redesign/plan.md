# Plan — template-phase3-redesign (기획 · 설계 · 작업 계획)

> 상태: **승인 대기(Proposed)**. 결정·계약은 `design-baseline.md`, 범위·인수 기준은 `charter.md`.

---

## 1. 기획 (무엇을, 누구를 위해)

| 항목 | 내용 |
|---|---|
| 주제 | 백엔드 개발자 한 명의 사이트: 포트폴리오(경력·학력·관심사·프로젝트·연락처) + 기술 글 5종(프로젝트·온라인 스터디·블로그·오픈소스·도서) + 게시판 3종 |
| 독자 | ① 채용 담당자·의뢰인(포트폴리오를 빠르게 훑음) ② 개발자(글을 끝까지 읽음, 코드 블록·표가 많음) |
| 주된 일 | 작업을 신뢰감 있게 보여 주고, 글을 편하게 읽게 한다 |
| 콘텐츠 특성 | 한·영 혼용(i18n), Summernote HTML 본문(제목·표·이미지·코드), 태그·좋아요·조회수·댓글(3단계 깊이) |
| 성공 기준 | 모든 페이지가 같은 디자인 언어, 첫 화면 전송량 절반 이하, 접근성 AA, 다크 모드 |

## 2. 디자인 방향 (초안 — 시안 2개 만들어 비교 후 확정, ADR-002)

frontend-design 지침의 흔한 기본값(크림 배경+테라코타, 검정+형광 강조, 신문형 0 radius, 같은 카드·같은 그림자 반복,
모든 제목 위 대문자 라벨, `·` 메타 연결, `→` 붙은 버튼)을 피하고 **"개발자의 작업 기록"이라는 주제**에서 출발한다.

### 방향 A — "엔지니어링 노트" (권장 출발점)
- **개념**: 잘 정리된 기술 노트. 읽기가 주인공, 장식은 최소. 정보 구조(날짜·종류·태그)가 시각 구조가 된다.
- **색** (라이트 / 다크)
  - `paper` #F6F7F9 / #161B26 — 차가운 회백 / 남색 기운의 어두운 면(순흑 아님)
  - `ink` #1D2433 / #E7EAF0 — 본문
  - `graphite` #5A6478 / #A3ACBD — 보조 텍스트
  - `line` #E2E5EB / #2A3140 — 구분선
  - `spoon` #E8505B(큰 요소) · #C23A44(링크·작은 글자, 흰 배경 대비 AA) — **기존 브랜드 코랄(#FF6B6B)을 계승·보정**
  - `code` #0F172A 배경 + 구문 강조 6색(다크/라이트 공용)
- **글꼴**: Pretendard Variable 한 가족(본문 400, 제목 650~720, 자간 -0.02em) + 코드 블록 전용 고정폭(JetBrains Mono 또는 D2Coding 중 택1).
  기본 17px, 비율 1.25, 본문 줄 길이 ≤ 68ch, 행간 1.7(한글).
- **레이아웃**: 왼쪽 정렬 편집형. 글 목록은 "카드 그리드" 대신 날짜 열이 있는 **행(row) 카드**, 프로젝트만 썸네일 카드.
  상세는 본문 68ch 단일 열 + 넓은 화면에서 오른쪽 목차/메타 고정.
- **기억에 남는 한 곳(대담함은 여기에만)**: 홈 히어로 = 큰 이름 타이포 + 실제 데이터로 채운 "지금 하는 일" 로그
  (최근 프로젝트·최근 글·공부 중인 주제, 날짜순). 홈만 진입 연출 1회.

### 방향 B — "청사진(Blueprint)"
- **개념**: 백엔드 아키텍처 도면. 히어로에 기술 스택(Django·Redis·RabbitMQ·FastAPI…)의 연결을 SVG 다이어그램으로.
- **색**: `deep` #14213D 히어로·푸터 면, `paper` #F7F8FB, `ink` #1B2436, 강조 `amber` #E9A23B(큰 요소)·#9A6410(글자 AA), 보조 `steel` #6B7A99
- **글꼴**: Pretendard Variable + 제목에 너비가 좁은 굵은 굴림(Pretendard 800, 자간 -0.03em), 코드 고정폭 1종
- **레이아웃**: 넓은 그리드, 미세한 모눈 배경은 히어로에만. 카드 모서리 8px, 테두리 중심(그림자 최소)
- **기억에 남는 한 곳**: 히어로 스택 다이어그램(노드에 마우스/포커스 시 관련 글 수 표시)

> 시안 단계에서 각 방향을 "비슷한 다른 사이트 의뢰였어도 똑같이 나왔을까?"로 재검토하고, 바꾼 부분과 이유를 문서에 남긴다.

## 3. 디자인 시스템 설계 (방향과 무관한 공통 골격)

### 3-1. 토큰 (`static/css/app.css`의 `@layer tokens`, INV-1)
| 그룹 | 단계 |
|---|---|
| 색 | 의미 이름만 사용: `--c-bg`, `--c-surface`, `--c-text`, `--c-text-muted`, `--c-line`, `--c-accent`, `--c-accent-text`, `--c-success/warn/danger`, `--c-code-bg` (라이트/다크 2벌) |
| 글자 | `--fs-1`~`--fs-7` (`clamp()` 유동형), `--fw-regular/medium/bold`, `--lh-tight/body`, `--font-sans`, `--font-mono` |
| 간격 | 4px 기반 `--sp-1`~`--sp-9` (4·8·12·16·24·32·48·64·96) |
| 반경 | `--r-sm` 6px(입력·버튼) · `--r-md` 12px(카드) · `--r-pill` 999px(태그) — 위계별로 다르게 |
| 그림자 | `--sh-0` 없음(평면 목록) · `--sh-1`(올라온 카드, 호버) · `--sh-2`(드롭다운·오프캔버스) |
| 모션 | `--dur-fast` 120ms · `--dur-base` 200ms · `--ease-out`, `@media (prefers-reduced-motion)`에서 0 |
| Bootstrap 연결 | `--bs-body-font-family`, `--bs-body-color`, `--bs-primary-rgb`, `--bs-border-radius`, `--bs-link-color` 등을 토큰으로 재정의 → Bootstrap 컴포넌트도 같은 값 |

### 3-2. CSS 파일 구조 (ADR-004)
```
static/
  vendor/bootstrap-5.3.8/        bootstrap.min.css, bootstrap.bundle.min.js (로컬, 버전 디렉터리)
  vendor/bootstrap-icons-1.13.1/ sprite.svg (사용 아이콘만 추린 SVG)
  fonts/pretendard/              PretendardVariable dynamic-subset woff2
  css/app.css                    @layer reset, vendor, tokens, base, components, utilities (토큰은 이 파일의 tokens 층)
  css/pages/{home,post,portfolio,auth,board}.css
  js/core.js                     모듈 진입점: theme, nav, csrf fetch, toast
  js/modules/{replies,like,visit,portfolio-timeline,reveal,copy-code}.js
```
- `base.html`: `{% block extra_css %}`, `{% block extra_js %}`, `<script type="module">`, 폰트 preload, `color-scheme` 메타
- Summernote: 폼 페이지에서만 `{{ form.media }}`(django-summernote iframe 모드가 자체 로드) — 전역 CDN 제거

### 3-3. 컴포넌트 (ADR-005, INV-2) — 같은 역할 = 같은 템플릿 + 같은 클래스
| 컴포넌트 | 템플릿 | 사용처(현재 서로 다른 마크업) |
|---|---|---|
| 카드 기반 `.c-card` | `components/card_*.html` | 아래 4변형의 공통: 표면·반경·패딩·포커스 링·링크 영역 |
| └ 글 카드 `--post`(행) | `card_post.html` | 홈 최신 글, 블로그 목록 4종, 검색 결과, 게시판 목록(표 → 행 목록) |
| └ 프로젝트 카드 `--project` | `card_project.html` | 홈 포트폴리오 캐러셀·About Projects, 프로젝트 목록, 포트폴리오 프로젝트 |
| └ 주제 카드 `--topic` | `card_topic.html` | 홈 "공부 중인 것"(8개), 포트폴리오 관심사·교육·도서 |
| └ 타임라인 항목 `--timeline` | `card_timeline.html` | 포트폴리오 경력(현재 JS 문자열 생성) |
| 섹션 머리 | `section_head.html` | 모든 섹션 제목(현재 h1/h2 혼재) |
| 메타 줄 | `meta.html` | 작성자·날짜·조회·좋아요·댓글 수(목록·상세 공통) |
| 태그 | `tag_list.html` | 상세·카드 |
| 페이지네이션 | `pagination.html` | 목록 페이지네이션 + 댓글 페이지네이션(현재 2종) |
| 댓글 스레드 | `comments.html` + `<template>` | 블로그·게시판 상세 |
| 본문 타이포 `.c-prose` | (클래스) | Summernote 본문: 제목·표·이미지·인용·코드(복사 버튼) |
| 폼 | `form_field.html` | 글 작성/수정, 로그인·회원가입·비밀번호 6종, 프로필 → Bootstrap 폼 + 토큰 |
| 인증 레이아웃 | `auth_layout.html` | login/register/forgot/reset/resend/update/replace 7페이지 공통 |
| 빈 상태·오류 | `empty.html`, `errors/error.html` | 글 없음, 400/403/404/500 |
| 사이트 머리·꼬리 | `header.html`, `footer.html` | Bootstrap navbar + offcanvas(현 커스텀 mobile_menu 대체), 테마 토글, 언어 전환, 검색, 건너뛰기 링크 |

### 3-4. JS 설계 (ADR-008)
- 원칙: 서버 렌더링 우선, JS는 점진적 향상. DOM 생성은 `<template>` 복제 + `textContent`(XSS 계약 C-2)
- `core.js`: `csrfFetch()`(쿠키 csrftoken), 테마 토글, 내비 활성 표시, 토스트
- `replies.js`: 목록 조회·작성·수정·삭제·페이지(현재 525줄 문자열 조립 → 템플릿 기반), 이벤트 위임(`data-action`)
- `like.js`, `visit.js`, `portfolio-timeline.js`(경력 JSON → `<template>`), `copy-code.js`, `reveal.js`(홈 1회)
- 캐러셀: Bootstrap Carousel 유지 또는 CSS scroll-snap(접근성·무게 비교 후 결정)

### 3-5. 품질 기준 (charter §3)
접근성 AA(대비·포커스 링·키보드·스킵 링크·모션 감소·폼 오류 연결), 성능(폰트 subset·preload, 이미지 WebP/srcset/lazy·크기 지정, 미사용 제거),
SEO(페이지별 title·description·OG를 글 데이터로 — 현재 전 페이지 동일 meta), 다크 모드, i18n 문자열 유지, 인쇄 스타일(글 상세).

## 4. 작업 계획 (단계 · 산출물 · STOP)

| 단계 | 작업 | 도구 | 산출물 | 멈춤 |
|---|---|---|---|---|
| **0. 준비** | ① 브랜치 `template-phase3-redesign`(9b24050 기반) ② **현재 기준선 측정**: Lighthouse 6페이지, axe, 전송량, 스크린샷(라이트, 3폭) ③ 미해결 결정 처리(스킬 위치·impeccable 엔진·shadcn 정리) | chrome-devtools MCP, Playwright(WSL), webapp-testing | `baseline.md` | — |
| **1. 디자인 확정** | ① DESIGN.md(토큰·원칙) 초안 ② 방향 A·B 정적 HTML 시안: 홈 히어로·글 카드·프로젝트 카드·상세 본문·폼·다크 모드 ③ 지침 기반 자기 비평(impeccable critique/audit 문서, frontend-design 기본값 점검) | frontend-design, impeccable(지침), gsd-sketch, Playwright MCP 캡처 | `docs/design/DESIGN.md`, `docs/design/sketches/{a,b}.html` + 스크린샷 | **STOP ①: 방향 선택·토큰 승인** |
| **2. 기반 교체** | Bootstrap 5.3.8·Bootstrap Icons sprite·Pretendard self-host, `app.css` 골격(토큰 층 포함), `base.html` 머리 재구성, header/footer/offcanvas/테마 토글/스킵 링크, 미사용 vendor 로드 제거 | context7·WebSearch(버전), djLint | 새 레이아웃이 모든 페이지에 적용(본문은 아직 구 스타일) | — |
| **3. 컴포넌트** | 3-3 표의 컴포넌트 템플릿 + CSS, 상태(호버·포커스·비활성·빈 값·긴 제목·이미지 없음) | frontend-design, impeccable(polish/harden 지침) | `templates/components/*`, `css/app.css` components 층, 컴포넌트 테스트 | — |
| **4a. 파일럿 페이지** | 홈 + 블로그 상세(+목록 1종) 적용 | Playwright MCP, chrome-devtools | 파일럿 스크린샷 3폭×2테마, Lighthouse·axe | **STOP ②: 파일럿 리뷰** |
| **4b. 전체 적용** | 블로그 목록·상세 5종, 게시판 3종, 폼, 검색, 인증 7, 프로필, 포트폴리오, 오류, 약관 2 | 동일 | 페이지별 스크린샷 | — |
| **5. JS 재작성** | 3-4 모듈, 인라인 onclick·전역 함수 제거, axios·AOS·WOW 등 제거 | Playwright MCP(상호작용 시나리오), webapp-testing | `static/js/core.js`·`modules/*`, 상호작용 테스트 | — |
| **6. 정리·최적화** | 구 CSS 3개·미사용 vendor 디렉터리 삭제, 이미지 최적화(django-imagekit 썸네일 활용), 페이지별 SEO 메타, (선택) CSP 준비 | css_usage·INV-1 검사 스크립트 | 삭제 목록(사용자 확인 후 삭제) | 이미지 삭제는 개별 확인 |
| **7. 검증·수렴** | 인수 기준 전부, 2단계 테스트 갱신(마크업 단언), security-review, CRP 기록, 커밋(푸시 X) | pytest(WSL), djLint, Lighthouse, axe, security-review | run-log·ledger | **STOP ③: 최종 보고** |

- 실행 중 계획 밖 수정이 필요하면 고치기 전에 멈추고 질문(C-1).
- 커밋 단위: 단계별 1~3개. 각 커밋 시점에 전체 테스트 통과.

## 5. 별도 트랙 B — 백엔드 버전 (ADR-010, 결정 필요)
- 현황: Django 4.2 LTS **2026-04 지원 종료**. 5.2 LTS는 보안 패치 2028-04까지, 6.0은 2027-04까지.
- 권장: **Django 5.2 LTS**로 업그레이드하는 별도 그룹(디자인과 다른 브랜치). allauth 0.58→65.x(설정·템플릿 큰 변경), django-summernote·django-redis·silk·imagekit 호환성 확인 필요.
- 순서 제안: 3단계 0~1단계(디자인 확정)와 병행 조사 → 디자인 2단계 착수 전 결정.

## 6. 위험과 대응
| 위험 | 대응 |
|---|---|
| Summernote 본문이 새 글꼴·`.c-prose`에서 깨짐(인라인 style·font 태그) | sanitize 허용 style 속성 범위 안에서 prose 규칙 작성, 실제 글 샘플로 시안 검증 |
| 화면 전면 변경으로 2단계 특성화 테스트 대량 실패 | 기능 단언(링크·폼·권한)은 유지, 마크업 단언만 새 계약으로 교체 — 단계 7에서 일괄 아님, 페이지 적용마다 갱신 |
| 상세 뷰 캐시(`user_auth`·`like_state` 공유, 2단계 X-001)가 새 UI에서도 버튼 노출 오류 | 사용자 결정 필요(뷰 수정은 C-3 예외) |
| Windows 앱 제어 정책·Chrome 확장 미연결 | 검증은 WSL Playwright·Playwright MCP 우선 |
| 디자인이 템플릿처럼 보임 | 시안 단계 자기 비평 + 사용자 선택(STOP ①), 기억에 남는 요소 1곳 원칙 |

## 7. 도구 사용 계획
| 도구 | 쓰는 단계 | 용도 |
|---|---|---|
| frontend-design | 1·3·4 | 방향·토큰·레이아웃, 흔한 기본값 회피 검토 |
| impeccable (지침 문서) | 1·3·4·7 | shape·critique·typeset·colorize·polish·harden·audit 절차. 엔진 실행·훅 등록은 별도 승인 시에만 |
| gsd-sketch | 1 | 버려도 되는 정적 HTML 시안 |
| Playwright MCP | 1·4·5·7 | 화면 확인, 상호작용 시나리오(메뉴·댓글·좋아요·폼·테마) |
| webapp-testing + WSL Playwright | 0·4·7 | 서버 띄워 다중 폭·테마 스크린샷 자동 촬영 |
| chrome-devtools MCP | 0·4·7 | Lighthouse, a11y, LCP 분석 (연결 안 되면 WSL Lighthouse) |
| djLint, pytest, security-review | 전 단계 | 구조·회귀·보안 |
