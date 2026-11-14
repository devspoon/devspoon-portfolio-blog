# Charter — phase6-small-cleanups (v0.1 / 2026-11-14)

## 1. 변경 대상
| 항목 | 파일 |
|---|---|
| N2+ | `blog/views/{blog,books,online_study,project}/*_forms.py`(초기값), 5개 폼 `clean_tag_set`(공용 함수 1개), `blog/models/blog.py` `tag_save` |
| M4 | `home/views/service/search.py` `queryset_tag_search` |
| M8 | `blog/models/blog.py` `auto_delete_file_on_save_for_blog`, `users/models.py` `auto_delete_file_on_save` |
| R3 | `custom_middlewares/middlewares/statistics.py` `resolve_field` |
| R2 | `users/views/users_forms.py`, `portfolio/forms.py` |
| 닉네임 | `users/models.py` `_ensure_profile` |
| N3 | 테스트만(늘어나는 곳이 있으면 그 admin) |
| 죽은 코드 | `blog/models/blog.py` `__table_name__` |

## 2. 계약
- INV-1: 태그가 있는 글을 수정 화면에서 그대로 저장하면 태그가 바뀌지 않는다(블로그 5종).
- INV-2: 태그 검색은 페이지마다 최대 10개, 제목에 검색어가 그대로 나온다.
- INV-3: 각 항목에 되돌리면 실패하는 테스트가 있다.
- INV-4: 전체 pytest 통과, `check` ERROR 0, 이쪽 앱 `makemigrations --check` No changes, runserver 점검표 통과.

## 3. 비범위
- 이미 합쳐진 태그·0으로 쌓인 mac 통계의 보정(D3), 파일 삭제를 커밋 뒤로 미루기(롤백 시 파일 유실), 세션 저장소 분리(7단계).
