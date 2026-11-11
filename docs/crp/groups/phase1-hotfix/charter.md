# Charter — phase1-hotfix  (Charter v0.1 / 2026-11-11)

> 검수의 닫힌 정의. 상위 기준은 `design-baseline.md`.

## 1. 인벤토리

| 영역 | 경로 | 종류 | 결함 |
|---|---|---|---|
| 블로그 상세 뷰 ×5 | `blog/views/{blog,books,online_study,opensource,project}/*_blog.py` (`get_context_data`, 약 82~137행) | 소스 | C1 |
| board 상세 뷰 ×3 | `board/views/{notice,visiter,reactivation}/*_board.py` (`get_context_data`, 약 80~116행) | 소스 | C1 |
| 블로그 댓글 목록 ×5 | `blog/views/*/*_reply.py` (`*ReplyListJsonView.get`, 약 60~80행) | 소스 | C1(댓글), N1 |
| board 댓글 목록 ×3 | `board/views/*/*_reply.py` (`*ReplyListJsonView.get`, 약 55~80행) | 소스 | C1(댓글), N1 |
| 블로그 댓글 시그널 | `blog/models/blog_reply.py:97-111` | 소스 | C2 |
| board 댓글 시그널 | `board/models/board_reply.py:61-71` | 소스 | C2(형제) |
| 개발 도구 import | `blog/views/books/books_blog.py:21`, `blog/views/online_study/online_study_blog.py:20` | 소스 | M2 |
| 신규 테스트 | `blog/tests/test_phase1_hotfix.py`, `board/test_phase1_hotfix.py` (예정) | 테스트 | 전체 |

> board 앱에는 `board/tests.py` 모듈이 있어 `board/tests/` 패키지를 만들 수 없다. pytest 수집 패턴(`test_*.py`)에 맞춰 앱 루트에 둔다.

- 수정 대상 소스 파일 **18개**, 신규 테스트 파일 **2개**(GATE 3 기대치)
- 템플릿(`templates/**/*_detail.html` 9개)과 `static/js/blog_apis.js`는 **수정하지 않는다**(ADR-001, ADR-004). 값의 의미만 바뀐다.

## 2. 계약
### 2-1. 지원 구성
- 설정 `config.settings.test`와 실제 Redis(CI의 redis 5). django-redis 전용 API(`ttl`, `iter_keys`, `delete_pattern`)를 쓰므로 LocMem 캐시로 대체하지 않는다.
- 전제: PR #9의 `conftest.py` 자동 캐시 초기화 fixture. **PR #9 병합 후 main을 기준으로 구현한다.**

### 2-2. 위협 모델
- 방어한다: 한 방문자의 요청자별 값이 다른 방문자에게 보이는 것, User 객체가 Redis에 저장되는 것, 비로그인·비작성자에게 수정·삭제 버튼이 보이는 것.
- 방어하지 않는다: GET으로 상태를 바꾸는 요청(CSRF)은 4단계, 캐시 키 오염과 무효화 race는 2단계에서 다룬다.

### 2-3. 불변식
- INV-1: 상세 응답의 `user_auth`는 `request.user.is_authenticated and request.user.pk == board.author_id`와 같다. 다른 사용자가 먼저 방문해 캐시를 채운 뒤에도 마찬가지다.
- INV-2: 블로그 상세 응답의 `like_state`는 그 요청자의 좋아요 여부와 같다. 비로그인이면 `False`다.
- INV-3: 이 그룹의 변경 이후 Redis에는 새로운 `*:user_auth`·`*:like_state` 키가 생기지 않는다.
- INV-4: 댓글 삭제가 성공하면 행이 사라지고 부모 글의 `reply_count`가 1 줄어든다. 단 0 아래로는 내려가지 않는다. 블로그 5개와 board 3개 댓글 모델 모두 해당한다.
- INV-5: 댓글 목록 API의 쿼리 수는 댓글 수와 상관없이 일정하다(N+1 없음).

### 2-4. 비목표
- 캐시 키 체계, TTL, 무효화 시점, 이웃 글 캐시(2단계)
- 삭제·숨김 글 노출 정책(2단계 설계에서 결정)
- GET→POST 전환, 댓글 생성 검증(4단계)
- `utils/email/sub_settings/` 같은 사용되지 않는 사본 정리

## 3. 인수 기준
- [ ] 신규 테스트 2개 파일이 CI(현 main + PR #9 기준)에서 실제로 실행되고 통과한다. SKIP 0
- [ ] 각 결함마다 회귀 테스트가 **수정 전 코드에서 실패**함을 확인한다(fail-on-revert). C2는 수정 전 `DoesNotExist`로 실패해야 한다.
- [ ] INV-1·2 → 사용자 A(작성자)가 먼저 방문하고 사용자 B와 비로그인이 나중에 방문하는 순서로 8개 상세 URL을 parametrize한 테스트
- [ ] INV-3 → 위 테스트 뒤 `cache.keys("*user_auth*")`, `cache.keys("*like_state*")`가 비어 있음
- [ ] INV-4 → 댓글 모델 8개 parametrize: 삭제 후 행 없음, `reply_count` 감소. `reply_count=0`이면 그대로 0
- [ ] INV-5 → `django_assert_num_queries`로 댓글 1개일 때와 5개일 때 쿼리 수가 같음(블로그·board 각 1개 모델 이상)
- [ ] M2 → `books_blog`, `online_study_blog` 모듈에 `isort` import 없음(`grep`), 기존 테스트 통과
- [ ] 기존 전체 테스트 통과(회귀 0)
- [ ] 불가침 제약 C-1~C-5 위반 없음

## 4. 변경 이력
- v0.1 (2026-11-11): 최초 작성.
