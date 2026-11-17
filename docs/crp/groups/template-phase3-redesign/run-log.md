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

### Round 5 — 2026-11-13 (base SHA: `37a296e`) — 7단계 검증·번역
- **트리거:** 사용자 "진행해줘" → 승인된 계획 7단계
- **번역(R-004):** `makemessages -l ko`(gettext는 우분투 공식 패키지를 홈 폴더에 풀어 사용, 시스템 미설치).
  fuzzy 58개는 엉뚱한 옛 번역이 붙어 전부 새로 번역 → 397/404 번역(미번역 7 = fast-api·vue.js·OS 이름 등 기술 용어).
  `msgfmt --check` 통과. 함께 고침: 글 폼 제목·탭 제목 16개 템플릿 `{% trans %}`, 회원가입 등 폼 라벨 `_()`.
  한국어 요청 시 남은 영어는 DB 메뉴 이름·시드 글 본문뿐(번역 파일 대상 아님)
- **발견·수정:** axe serious — Summernote iframe `title` 없음(글 폼 3종) → `templates/django_summernote/widget_iframe.html`
  덮어쓰기(0.8.20.0 원본과 title만 다름). moderate — 약관 2쪽 h1 없음 → 제목 h1 추가.
  회귀 테스트 7개(fail-on-revert: 되돌리면 7 failed, 복원 7 passed). `post_form.html` 분기마다 반복된 label 1개로
- **검증:** pytest 156 passed·1 skipped / axe 22쪽 × 라이트·다크 × 360·1366 위반 0 /
  전송량 CSS+JS+폰트 983~994KB(기준 2,379KB, -59%, 목표 ≤1,190KB 통과. 이 중 491KB는 Google 애널리틱스) /
  INV-1 색 리터럴 0 / 미사용 CSS 클래스 0.9%(1/114) / djLint 구조 규칙: H025 1건은 if 블록 안에서 짝이 맞는 오탐 /
  보안: 브랜치 diff의 `|safe`·`mark_safe`·`format_html`은 계약 범위(관리자 입력·nh3 후처리·자동 이스케이프), 신규 취약점 0
- **Lighthouse 모바일(성능 포함, CLI 12.6.1):**
  | 페이지 | 압축 없음(runserver) P·A·BP·SEO | gzip 프록시 P |
  |---|---|---|
  | 홈 | 78·100·100·100 | 85 |
  | 블로그 목록 | 70·100·96·100 | 96 |
  | 블로그 상세 | 79·100·93·100 | 측정 실패(NO_NAVSTART) |
  | 공지 목록 | 76·100·100·100 | 84 |
  | 공지 상세 | 77·100·93·100 | 88 |
  | 로그인 | 77·100·96·100 | 96 |
  | 포트폴리오 | 74·100·96·100 | 95 |
  성능 ≥90 **미달**. 원인: 정적 파일 무압축(316KB), Bootstrap CSS 대부분 미사용(219KB), 애널리틱스 긴 작업,
  LCP 렌더링 지연 ~2.4초(렌더링 차단 CSS + 웹폰트 교체), 홈 CLS 0.097(글꼴 교체로 `.p-now` 밀림). BP 93~96은 R-007·R-011
- **범위 밖 발견(보고만):** `config/settings/sub_settings/cloud/aws.py`에 AWS 접근 키·비밀 키 평문(2022 첫 커밋부터 git, 어디서도 import 안 함) — R-014
- **수렴 판정:** `NOT CONVERGED` — 성능 인수 기준 미달(R-013), 스크린샷 세트 사용자 확인 대기(STOP ③)
- **잔여 위험 변화:** R-004 해소, R-013·R-014 추가

### Round 6 — 2026-11-13 (base SHA: `df41a88`) — R-013 대응 B안(글꼴 로딩)
- **트리거:** 사용자 "B로 진행해줘"
- **조사:** 한국어 화면은 Pretendard 조각 7~8개(약 176KB, woff2라 gzip 무효)를 받음. 글꼴 CSS(56KB, gzip 13KB)가 렌더링 차단
- **실험(코드 무변경, 프록시가 응답만 고쳐 씀, Lighthouse 모바일·한국어·3회 중앙값):**
  | 방식 | 홈 P/LCP | 공지 목록 P/LCP | 블로그 상세 P/LCP |
  |---|---|---|---|
  | 현재 | 93 / 1.96s | 95 / 1.53s | 93 / 2.53s |
  | 조각 preload | 92 / 2.90s | 94 / 2.78s | 93 / 2.97s |
  | font-display optional | 91 / 2.89s | 95 / 1.65s | 91 / 2.87s |
  | **글꼴 CSS 비차단** | **95 / 1.51s** | **96 / 1.62s** | **96 / 1.83s** |
  | optional+preload | 92 / 2.98s | 93 / 2.75s | 93 / 3.01s |
  preload는 글꼴 7개가 CSS와 대역폭을 다퉈 LCP가 오히려 늘어 기각. 영어 화면 홈 CLS 0.097 → 비차단에서 0
- **적용:** `base.html` 글꼴 CSS `media="print" onload` + `<noscript>` 대체 링크(JS 꺼짐에서도 글꼴 적용). 회귀 테스트 1개(fail-on-revert)
- **검증:** pytest 157 passed·1 skipped / axe 위반 0 / Lighthouse gzip·한국어 3회 중앙값: 홈 97, 블로그 목록 98, 블로그 상세 99,
  공지 목록 97, 공지 상세 99, 로그인 99, 포트폴리오 99(5회). 개별 회차 74~84가 가끔 섞임 — 출처 불명 긴 작업 1.4s·첫 응답 지연(측정 PC·runserver 잡음).
  A100·SEO100 유지, BP 93~100(R-007·R-011)
- **수렴 판정:** `NOT CONVERGED` — 성능은 압축 전제에서 통과, 운영 압축 여부 미확인(R-013), 스크린샷 세트 사용자 확인 대기
- **잔여 위험 변화:** R-013 조건부 해소로 변경

### Round 7 — 2026-11-14 (base SHA: `54976ab`) — 스크린샷 검토 세트
- **트리거:** 사용자 "작업 재개해줘" → charter §3 마지막 항목(스크린샷 세트 사용자 확인)
- **세트:** 12쪽(홈·블로그 목록·블로그 상세(운영진)·공지 목록·공지 상세·검색·포트폴리오·로그인·회원가입·프로필·글쓰기·404) × 라이트·다크 × 360·768·1366 = 72장,
  페이지별 모음 이미지 12장. 검색은 SQLite가 UNION을 못 돌려, 같은 모델별 쿼리를 Python에서 합친 결과로 렌더링 후 같은 출처에서 촬영
- **발견·수정:** 상세 작성자 칸 — 닉네임이 빈 계정이면 빈 `<span>`이 간격을 차지해 날짜가 밀림 → 닉네임 있을 때만 출력
  (username으로 대신하지 않음: 로그인 ID 노출 방지). 회귀 테스트 5개(fail-on-revert)
- **범위 밖 발견(보고만):** ① 태그 검색 뷰가 `tag`에 QuerySet을 넣어 제목이 `<QuerySet ...>`로 나오고, 결과를 페이지로 나누지 않음
  (`home/views/service/search.py` `queryset_tag_search`) ② 글 폼 라벨이 모델 필드 이름(`dev_lang`, `file1`) ③ 다크 모드에서 Summernote 편집 영역 흰색(iframe 내부 CSS)
- **검증:** pytest 162 passed·1 skipped
- **수렴 판정:** `NOT CONVERGED` — 스크린샷 세트 사용자 확인 대기(STOP ③)

### Round 8 — 2026-11-14 (base SHA: `726d55d`) — 범위 밖 발견 수정(REQ-009)
- **트리거:** 사용자 "2번 진행해줘" → 설계 승인 "권장대로 진행해줘"(태그 공백 제거 포함)
- **수정(모두 실패 테스트 먼저):**
  1. 태그 수정 손상(형제 버그, 데이터): blog·books·online_study·project 폼이 수정 화면 태그를 `"".join`으로 채워, 그대로 저장하면
     태그가 하나로 합쳐짐 → `",".join`. `tag_save`는 앞뒤 공백 제거·중복 제거, 빈 입력은 여전히 태그 전부 삭제(기존 동작 유지), 죽은 `re.findall` 삭제
  2. 폼 라벨 8개 폼: 필드 이름 → `_()` 단어(한국어 번역). 연결점 `post_form.html`의 `field.label == 'file1'` → `field.name`,
     같은 유형 `form_field.html`의 `field.label == "Captcha"` → `field.name`. 번역 변경: Content 콘텐츠→본문, Priority 우선 사항→우선순위
  3. 태그 검색: 컨텍스트 `tag`가 QuerySet이던 것을 검색어 문자열로, `board`를 페이지 결과로
  4. 다크 편집기: `SUMMERNOTE_CONFIG` css/js에 `summernote-theme.{css,js}` — iframe이 부모 페이지의 `data-bs-theme`와 색 토큰을 복사(색 리터럴 없음, INV-1),
     테마 전환을 MutationObserver로 따라감. 확인 중 bs4 `.card` 흰 배경 띠 발견해 함께 처리
- **회귀 테스트:** test_tags 7, test_form_labels 9, test_search 1, test_editor_theme 1 — 모두 수정 전 실패 확인
- **검증:** pytest 180 passed·1 skipped / axe 위반 0 / 다크 글쓰기 화면: 편집기 배경 = 다크 `--c-surface`, 전환 후 라이트 복귀 / 번역 402/409
- **잔여:** 이미 공백이 붙어 저장된 태그는 그대로(데이터 정리는 범위 밖)

### Round 9 — 2026-11-16 (base SHA: `f094739`) — 기존 공백 태그 정리(REQ-010)
- **트리거:** 사용자 "권장 방식으로 공백 제거까지 함께 진행해줘" → 데이터 정리 방식 결정
- **폐기한 안:** 데이터 마이그레이션(테스트 3개 통과까지 작성) — `.gitignore`가 `migrations/`를 제외하고 각 환경이
  `makemigrations`로 생성하므로 배포되지 않고, 운영 마이그레이션 이름이 달라 의존이 깨질 수 있음. 커밋 전 삭제
- **운영 DB 조회(읽기 전용):** 저장소 루트 `.env` = 운영 PostgreSQL(PgBouncer 6432). `BEGIN READ ONLY`·SELECT만·ROLLBACK, 접속 정보 비출력.
  태그 35개 중 앞뒤 공백 3개(`'  '`, `' a'`, `' c'`), 셋 다 연결된 글 0 → 지워도 글 영향 없음
- **결정:** 코드 없이 관리자 화면에서 사용자가 3개 삭제. 저장 시 공백 제거(`f094739`)로 재발 없음
- **정정:** 운영 DB는 MySQL이 아니라 PostgreSQL(R-011 문구 수정, 백업은 `pg_dump`)

### Round 10 — 2026-11-17 (base SHA: `0c2ae8d`) — 남은 4가지(REQ-011)
- **R-012 해소:** 운영 PostgreSQL(스키마 `django_portfolio_blog`) 읽기 전용 조회 — 텍스트 컬럼 239개, `static/images/` 언급 0, 삭제 이미지 54개 참조 0
- **R-013 해소:** 운영 `https://www.devspoon.com` HEAD 요청 — HTML·CSS·JS 모두 `Content-Encoding: gzip`. nginx 설정 작업 불필요
- **R-015 신규:** 같은 응답의 `Cache-Control: max-age=315360000`(10년) + 해시 없는 파일 이름 → 이후 수정 시 재방문자에게 옛 파일. 설계안:
  A) `ManifestStaticFilesStorage`(해시 파일명, ES 모듈 import 재작성 필요·collectstatic 필수 — 배포 구조 확인 전제),
  B) nginx 정적 파일 캐시를 재검증 방식으로(`devspoon-web` 저장소, 사용자 작업), C) 템플릿 링크에 버전 쿼리(`?v=`) — 모듈 import 내부는 못 바꿈
- **Django 5.2(트랙 B):** 하위 에이전트 조사 + 운영 PostgreSQL 17.5 확인 → `../django-52-upgrade/plan.md`(막힘 3: celery-beat 2.7, Django 제약, recaptcha 3.0)
- **작은 개선 설계:** R-007 소셜 버튼 — 각 사 공식 2x 이미지 + `srcset`(외부 파일 내려받기 승인 필요, Google은 현재 'pressed' 상태 이미지라 기본 상태로 교체);
  R-009 `/portfolio/json/` — 저장소 내 사용처 0, 화면 뷰와 독립 → 뷰·URL 삭제(외부 사용 여부는 미확인);
  R-010 새 댓글 — `comments.js`만 수정: 작성 직전 sessionStorage에 표시, 상세 재로드 시 최상위 댓글이면 마지막 페이지·답글이면 작성 당시 페이지를 불러오고 댓글 영역으로 이동
- **수렴 판정:** `NOT CONVERGED` — R-015·작은 개선·트랙 B 승인 대기

### Round 11 — 2026-11-17 (base SHA: `c480972`) — 권장 순서 1단계(R-009·R-010)
- **트리거:** 사용자 "전체 권장 방식으로 진행해줘" — 1) R-009·R-010 구현, 2) nginx 캐시·공백 태그 3개·소셜 버튼 이미지·push/배포는 사용자, 3) Django 5.2는 배포 후 별도 브랜치
- **R-009:** `WorkExperienceJsonView`·`portfolio/json/`·미사용 `JsonResponse` import 삭제. 테스트 2개(삭제 전 실패 확인)
- **R-010:** `comments.js`만 수정(서버·캐시 무변경, 작성 시 목록 캐시는 기존대로 삭제됨). 저장소 차단 시 1페이지(기존 동작)
- **검증:** pytest 182 passed·1 skipped / Playwright 시나리오(댓글 12개 글): 최상위 작성 → 2페이지·새 댓글 보임 3/3, 답글 → 1페이지·부모 아래 3/3, 일반 새로고침 → 1페이지 2/2.
  실패 회차는 모두 서버 500 — 요청 기록 미들웨어의 SQLite 쓰기가 아바타(media 404)·방문 집계 요청과 겹침(R-011, 단독 호출은 200). 검증 스크립트는 방문 집계·media 요청을 브라우저에서 응답 처리해 격리
- **수렴 판정:** `NOT CONVERGED` — 사용자 작업(nginx·태그·이미지·배포)과 R-015 대기

### Round 12 — 2026-11-17 (base SHA: `216a396`) — 소셜 로그인 버튼(R-007)
- **트리거:** 사용자 "구글·카카오는 받아서 적용하고 네이버는 bi.md에서 받을 수 있는 이미지 검토"
- **내려받기(승인됨, 프로젝트 밖 빈 폴더):** Google `signin-assets.zip`(835KB, developers.google.com) — Dark·텍스트·사각형 @3x 사용,
  Kakao `kakao_login_large_narrow.png`(6.6KB, developers.kakao.com). PIL로 형식·크기 확인 후 `static/images/`로
- **적용:** `login.html` 두 버튼 교체 + width/height(CLS 방지). 이전 `btn_google_signin_dark_pressed_web.png`(눌린 상태)·`kakao_login_medium_narrow.png` 삭제.
  테스트 1개(이미지 존재·높이 ≥ 88px, 되돌리면 실패 확인)
- **검증:** pytest 183 passed·1 skipped / Lighthouse 로그인 image-size-responsive 지적은 네이버 1건만 남음 / 360폭 화면 확인
- **네이버 검토(bi.md 원본):** 자료 `NAVER_login_KR.zip`(PNG, 196KB)·`NAVER_login_EN.zip`(279KB)·`.ai`·`.fig`. 규칙: 지정 컬러 고정(녹색 #03A94D 권장,
  흰색 배경 허용), 완성형 권장, N 로고 16px 이상, 문구 변경 가능, **타사 버튼이 컬러일 때 흰색 버튼 지양**, 타사 버튼보다 작게 쓰지 말 것

- **네이버 적용(사용자 승인 "권장 방식으로 진행"):** `NAVER_login_KR.zip`(196KB) → `NAVER_login_Light_KR_green_narrow_H48.png`(840×192, #03A94D)를
  `naver_login_green.png`로. 흰색 `naver_btnW_official.png` 삭제. H48 버튼을 44px로 줄이면 N 로고가 16px 미만이 되므로 `.c-social img` 높이 44→48px,
  세 버튼 width/height 216·195·210×48. 테스트 기준을 Lighthouse 규칙(표시 높이의 1.5배 = 72px 이상)으로, 네이버 예외 제거
- **검증:** pytest 183 passed·1 skipped / 로그인 Lighthouse BP 100(image-size-responsive 통과)·CLS 0 / 라이트·다크 360폭 화면 확인

### Round 13 — 2026-11-17 (base SHA: `caa21b8`) — 운영 공백 태그 삭제(REQ-010)
- **트리거:** 사용자 "삭제 진행해줘"(관리자 화면 대신 Claude가 직접 삭제 — 명시 승인)
- **동등성:** `TagAdmin`은 기본 `ModelAdmin`, `Tag`에 삭제 신호·캐시 정리 없음 → SQL 삭제 = 관리자 삭제
- **방법:** 작업 폴더 스크립트 하나, 접속 정보 비출력. `tag`를 참조하는 외래키를 카탈로그에서 찾아(5개 `*_post_tag_set`) 연결 0 재확인,
  `FOR UPDATE`로 잠근 뒤 `id = ANY(...) AND NOT EXISTS(연결)` 조건 삭제, 정확히 3건일 때만 COMMIT. 연습 실행(ROLLBACK) 먼저
- **삭제 전 기록(복구용):** `id=6 ' c'`, `id=7 ' a'`, `id=32 '  '` — 셋 다 연결 0
- **사후 확인(별도 읽기 전용 연결):** 태그 32개, 앞뒤 공백 태그 0

## 심각도 추세 (수렴이 보이게)
| Round | CRIT | HIGH | MED | LOW | 신규 Fix | 판정 |
|---|---|---|---|---|---|---|
| 1 |  |  |  |  |  |  |
