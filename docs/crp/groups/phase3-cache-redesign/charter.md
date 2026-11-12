# Charter — phase3-cache-redesign  (Charter v0.1 / 2026-11-12)

> 상위 기준은 `design-baseline.md`.

## 1. 인벤토리

### 1-1. 캐시 사용처와 바뀌는 방식

| 사용처 | 지금 | 바뀐 뒤 |
|---|---|---|
| 상세 뷰 8개(`blog/views/{blog,books,online_study,opensource,project}/*_blog.py`, `board/views/{notice,visiter,reactivation}/*_board.py`) | QuerySet 전체·이웃 글을 글 pk별 키에 저장, 히트마다 `ttl`+`get`+SCAN | (D2-A) 캐시 없음. `activate_objects`(D1-A)로 조회, 이웃 글도 `activate_objects` |
| 댓글 목록 뷰 8개(`*_reply.py`의 `*ReplyListJsonView`) | `prefix:pk:<원본 page>` 키, 무효화는 `delete_pattern` | `v2:replies:<app.model>:<post_pk>:<ver>:<page>`, 무효화는 버전 키 삭제 1회 |
| `home/views/index.py` | `index:0:*` 여러 키, 히트마다 SCAN | `v2:index` dict 1개 |
| `portfolio/views.py`(`PortfolioView`, `WorkExperienceJsonView`) | `portfolio:<lang idx>:0:*` 여러 키 + SCAN, 경력은 언어 없는 키 | `v2:portfolio:<lang>`·`v2:portfolio:work:<lang>` |
| `home/templatetags/home_tag.py` | `home:main_menu:0:main_menu`, `home:site_info:0:site_info` | `v2:home:main_menu`, `v2:home:site_info` |
| 무효화: 뷰의 수동 삭제, `index_cache_clean`, admin mixin 4종 | 저장 전·커밋 전 삭제, 일괄 액션 누락, 접두사 오타 | 시그널 + `on_commit` 한 곳(`common/cache_invalidation.py`), admin 일괄 액션은 같은 함수 호출 |

### 1-2. 코드 수정 예정 파일

| 파일 | 이유 |
|---|---|
| `common/components/django_redis_cache_components.py` | 키 함수·읽기 함수로 교체, `dredis_*` 삭제(ADR-002·008) |
| `common/cache_invalidation.py`(신규), `common/apps.py` 또는 각 앱 `apps.py` | 시그널 등록(ADR-003) |
| `common/mixin/views/`(신규 `post_detail.py`, `reply_list.py`) | mixin(ADR-008) |
| 상세 뷰 8개, 댓글 뷰 8개 | mixin 사용, 수동 캐시 삭제·`index_cache_clean` 제거 |
| `common/mixin/admin/redis_cache_handler.py` | 저장·삭제 시 수동 삭제 제거, 일괄 액션에 무효화 추가, 오타 접두사 의존 제거 |
| `common/decorators/cache.py` | 삭제(ADR-008) |
| `board/admin/*_admin.py`, `blog/admin/*_admin.py`, `portfolio/admin.py`, `home/admin/default_admin.py`, `users/admin.py` | `cache_prefix`·`view_keys`·`use_pk` 속성 정리(필요한 곳만) |
| `home/views/index.py`, `portfolio/views.py`, `home/templatetags/home_tag.py` | 키 1개 읽기(ADR-002·007) |
| `blog/tests/test_phase1_hotfix.py`, `board/test_phase1_hotfix.py` | 옛 키 이름 확인을 새 키로 바꿈(C-1) |
| 신규 테스트 `common/tests/test_cache_*.py` 등 | 아래 불변식 |

## 2. 계약
### 2-1. 지원 구성
- Python 3.12, `config.settings.test`(SQLite + Redis)로 pytest, `config.settings.dev`(PostgreSQL + Redis)로 runserver. Redis는 WSL 컨테이너 `devspoon-redis`.
### 2-2. 위협 모델
- 방어한다: 삭제·숨김 글이 상세 URL·이웃 링크·index로 새는 것(D1), 요청자별 값의 캐시 저장(phase1 C1 회귀), 한 언어의 데이터가 다른 언어로 나가는 것, 쓰기 뒤 옛 값이 남는 것, 요청 경로 SCAN으로 인한 Redis 지연(세션과 같은 DB).
- 방어하지 않는다: 캐시 서버 장애 시 동작(지금도 django-redis 기본 동작에 맡김), 방문 수·좋아요 수의 index 표시 지연(R-001).
### 2-3. 불변식
- INV-1: 전체 pytest 통과(테스트 수는 줄지 않는다).
- INV-2: `manage.py check --settings=config.settings.dev` ERROR 없음.
- INV-3: 우리 앱 `makemigrations --check --dry-run` No changes.
- INV-4: runserver 점검표(§3) 통과.
- INV-5: 요청 경로(상세·댓글 목록·index·portfolio·경력 JSON·메뉴·사이트 정보·글/댓글 작성·수정·삭제)에서 `keys`·`iter_keys`·`delete_pattern`이 한 번도 불리지 않는다(테스트에서 감시). 캐시 히트의 Redis 호출은 키당 `get` 1회(댓글 목록은 버전 포함 2회).
- INV-6: 아래 쓰기 경로마다, 커밋 뒤에 해당 캐시가 무효화된다(테스트): 글 작성·수정·삭제 뷰, 댓글 작성·수정·삭제 뷰, admin 저장·삭제·"선택 삭제", admin 삭제·숨김·복구·공개 액션, 메뉴·사이트 정보 저장과 mptt 이동, portfolio 모델 저장·삭제. 롤백된 쓰기는 무효화하지 않아도 되지만, 커밋 전에 지우지는 않는다.
- INV-7: 캐시에 요청자별 값(`user_auth`·`like_state`·User 객체·폼 인스턴스)이 없다(phase1 불변식 승계).
### 2-4. 비목표
- 세션 저장소 분리(7단계), GET→POST 전환·좋아요 race(5단계), 데이터 migration(4단계), 방문 수·좋아요 수 집계 방식 변경.

## 3. 인수 기준
- [x] F-001~F-010 Fixed, 각 수정에 수정 전 실패한 테스트가 있다
- [x] INV-1~7 통과
- [x] 요청 경로 코드에 `dredis_`·`iter_keys`·`delete_pattern`(admin 수동 액션 제외)·`index_cache_clean`이 남아 있지 않다(grep 0건)
- [x] runserver 점검표: 2단계 점검표 전부 + 삭제·숨김 글 상세 404(D1-A일 때) · 이웃 링크에 삭제 글 없음 · admin 숨김 액션 직후 index에서 사라짐 · 경력 JSON 언어별 · 댓글 목록 `?page` 없이 200 · 게시판 댓글 admin 저장 200 · `redis-cli MONITOR`로 점검표 요청 중 `SCAN` 0회
- [x] 불가침 제약 C-1~C-7 위반 없음

## 4. 변경 이력
- v0.2 (2026-11-12): 인수 기준 충족(Round 1).
- v0.1 (2026-11-12): 최초 작성.
