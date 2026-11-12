# Charter — template-phase2-structure  (Charter v0.1 / 2026-11-11)

> 상위 기준: `design-baseline.md`

## 1. 인벤토리
| 영역 | 경로 | 변경 | ADR |
|---|---|---|---|
| 블로그 상세 5 | `templates/blog/*/*_detail.html` → 공통 `templates/blog/_post_detail.html` | 통합 | 001·004·006 |
| 게시판 상세 3 | `templates/board/*/*_detail.html` → 공통 `templates/board/_board_detail.html` | 통합 | 001·004·006 |
| 작성·수정 폼 16 | `templates/{blog,board}/*/*_{edit,update}.html` → 공통 `templates/base/post_form.html` | 통합 | 002·007 |
| 목록 2 + ListView 8 | `templates/blog/blog_list.html`, `templates/board/board_list.html`, `*ListView.extra_context` | 서버 렌더링 | 003 |
| 레이아웃 | `templates/base/{base,meta,header,mobile_menu,pagenation}.html` | 결함 수정 | 005 |
| 기타 페이지 | `templates/{home/index,portfolio/portfolio,users/login,users/profile,users/password_replacement}.html` | alt·중첩 수정 | 005 |
| JS | `static/js/blog.js` (URL 재작성 블록 3개 삭제) | 삭제 | 003·004 |
| 테스트(신규) | `blog/tests/test_templates.py`, `board/test_templates.py`, `home/tests/test_layout.py` | 특성화·회귀 | — |

예상 템플릿 수: 61 → 상세·폼 자식은 남으나(뷰 template_name 유지) 각 3~15줄. 중복 본문 약 1,500줄 → 공통 3개 파일.

## 2. 계약
### 2-3. 불변식
- INV-1: 모든 페이지가 같은 데이터로 같은 정보(제목·메타·본문·버튼·링크)를 렌더링한다(특성화 테스트)
- INV-2: 페이지당 `<title>` 1개, `<main>` 1개, 목록·상세는 `<h1>` 1개 (v0.2: 폼 페이지 `<h1>`은 3단계로 — ADR-012)
- INV-3: 내부 링크는 `{% url %}`로 생성(목록·상세·이전/다음·작성), JS가 href를 다시 쓰지 않는다
- INV-4: djLint 구조 규칙(H025 태그 짝, H037 중복 속성, H054 중첩 대화형, H043 버튼 type, H013 alt) — 이번에 고친 줄에서 위반 0 (v0.2: 기존 결함 8건은 R-001)
- INV-5: 1단계 보안 테스트 98개 그대로 통과
### 2-4. 비목표
- CSS 통합·토큰(3단계), JS 구조 개편(4단계, 이번엔 죽은 코드만 삭제), 디자인 변경(5단계)
- 필드 렌더링 방식(`{{ field }}`/crispy 등), 문구·번역 개편, 관리자·이메일 템플릿
- djLint T001(변수 공백) 등 서식 규칙 일괄 포맷(diff 폭증 — 선택 사항 Q4)

## 3. 인수 기준
- [ ] 특성화 테스트를 **변경 전에** 작성해 통과(green) → 변경 후에도 통과
- [ ] 전체 pytest(WSL) 통과, 1단계 98개 포함
- [ ] djLint 대상 템플릿 구조 규칙 위반 0
- [ ] (Q3 승인 시) 변경 전·후 주요 화면 스크린샷 비교에서 시각 차이 없음
- [ ] security-review: 신규 취약점 0

## 4. 변경 이력
- v0.1 (2026-11-11): 최초 작성.
- v0.2 (2026-11-11): INV-2·INV-4 범위 축소(ADR-012, R-001) — C-2 우선.
