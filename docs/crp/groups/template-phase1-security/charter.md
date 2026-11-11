# Charter — template-phase1-security  (Charter v0.1 / 2026-11-11)

> 상위 기준: `design-baseline.md` (모순 시 design-baseline 우선)

## 1. 인벤토리
| 영역 | 경로 | 종류 | 비고 |
|---|---|---|---|
| 게시글 Delete·Like 뷰 | `blog/views/*/*_blog.py`(5), `board/views/*/*_board.py`(3) | 소스 | ADR-001 |
| 댓글 Delete 뷰 | `blog/views/*/*_reply.py`(5), `board/views/*/*_reply.py`(3) | 소스 | ADR-001 |
| 회원 탈퇴 뷰 | `users/views/users.py` `UserDeleteView` | 소스 | ADR-001 |
| 상세 템플릿 | `templates/blog/*/*_detail.html`(5), `templates/board/*/*_detail.html`(3) | 템플릿 | ADR-003·005 |
| 홈·프로필 | `templates/home/index.html`, `templates/users/profile.html` | 템플릿 | ADR-003·005 |
| JS | `static/js/blog.js`, `static/js/blog_apis.js` | 소스 | ADR-002·005 |
| 필터 | `public_tags` 템플릿 태그 모듈 | 소스 | ADR-003 |
| 의존성 | `pyproject.toml`, `poetry.lock`, `requirements/dev.txt` | 설정 | nh3 |
| 테스트(신규) | `blog/tests/test_security.py`, `board/tests/…`, `users/tests/test_user_delete.py`, `home/tests/test_render_smoke.py` | 테스트 | |

## 2. 계약
### 2-2. 위협 모델
- 방어한다: 로그인 회원이 넣은 본문·댓글의 저장형 XSS / 외부 사이트에서의 GET 기반 삭제·탈퇴·좋아요(CSRF)
- 방어하지 않는다: 관리자만 입력하는 포트폴리오·약관 `|safe`(residual-risk), CSP 헤더(후속)
### 2-3. 불변식
- INV-1: 상태를 바꾸는 엔드포인트는 GET에 405를 반환하고 데이터가 바뀌지 않는다
- INV-2: 사용자 입력 HTML은 `sanitize_html`을 거친 뒤에만 출력된다(`<script>`, `on*` 속성, `javascript:` URL 없음)
- INV-3: 댓글 문자열은 DOM에 HTML로 해석되지 않는다
### 2-4. 비목표
- 디자인 변경, 템플릿 통합(2단계), JS 구조 개편(4단계), CSP 도입

## 3. 인수 기준
- [ ] 신규·기존 pytest 전부 실제 실행·통과
- [ ] INV-1: 21개 뷰(Delete 16 + 탈퇴 1 + Like 5 중 해당분) × GET=405 파라미터화 테스트
- [ ] INV-2: 필터 단위 테스트(악성 제거 + Summernote 서식 유지) + 상세 페이지 렌더 테스트
- [ ] INV-3: 브라우저에서 `<img src=x onerror=…>` 댓글이 텍스트로 보이는지 확인(또는 node assert)
- [ ] 렌더 안전망: 홈·목록 8·상세 8·작성 폼 200 응답
- [ ] security-review 통과

## 4. 변경 이력
- v0.1 (2026-11-11): 최초 작성.
