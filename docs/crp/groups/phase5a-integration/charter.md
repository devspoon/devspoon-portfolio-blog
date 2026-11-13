# Charter — phase5a-integration  (Charter v0.1 / 2026-11-13)

> 상위 기준은 `design-baseline.md`.

## 1. 인벤토리 — 충돌 18개 파일의 해결

| 파일 | 해결 |
|---|---|
| `blog/views/*/*_blog.py` 5, `board/views/*/*_board.py` 3 | 이쪽 상세 mixin·좋아요 잠금 유지 + 그쪽 `StaffRequiredMixin`(블로그 5·공지), POST 전용 삭제·좋아요, 목록 `extra_context` |
| `blog/models/blog_reply.py`, `board/models/board_reply.py` | 같은 수정(댓글 삭제 시그널). 이쪽 구현 유지 |
| `common/error/error_views.py` | 같은 수정(에러 상태 코드). 그쪽 구현(더 짧음) |
| `home/views/index.py` | 이쪽 구조 + 그쪽 결정(최신순, `author` 제외) |
| `portfolio/views.py` | 이쪽 구조 + 그쪽 `stack`·`experience` |
| `pyproject.toml`·`poetry.lock`·`requirements/dev.txt` | 이쪽 기준 + `poetry add nh3`(0.3.7)·`djlint ~1.36`(1.36.4) + `[tool.djlint]`, dev.txt는 export. 기존 패키지 버전 변경 0 |
| `templates/base/search_result_board_list.html`, `templates/portfolio/portfolio.html` | 그쪽 새 마크업 + 이쪽 `board_type`, 문의 폼 captcha·길이 제한 |
| (충돌 아님) `common/mixin/views.py` | 패키지로 이동(F-001) |

## 2. 계약
- 불변식: INV-1 양쪽 테스트 전부 통과 · INV-2 `check` ERROR 없음 · INV-3 `makemigrations --check` No changes · INV-4 runserver 점검표(POST·CSRF로 갱신) · INV-5 요청 처리 중 SCAN 0(이쪽 phase3) · INV-6 POST 전용 상태 변경(그쪽 phase1)

## 3. 인수 기준
- [x] 충돌 18개 + 이름 충돌 1개 해결, 충돌 표시 0
- [x] INV-1~6 통과
- [x] 그쪽 결정과 다른 사용자 동작을 고른 곳 없음(F-006은 결정 승계)

## 4. 변경 이력
- v0.1 (2026-11-13): 최초 작성.
