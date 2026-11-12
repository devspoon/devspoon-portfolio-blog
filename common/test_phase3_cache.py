"""3단계 캐시 재설계 회귀 테스트 (docs/crp/groups/phase3-cache-redesign).

쓰기 뒤 무효화는 커밋 뒤(on_commit)에 일어나므로 쓰기는
django_capture_on_commit_callbacks(execute=True) 안에서 한다.
"""
import datetime

import pytest
from django.contrib import admin
from django.core.cache import cache
from django.db.models.query import QuerySet
from django.test import Client
from django.urls import reverse
from django_redis.cache import RedisCache

from blog.models.blog import BlogPost, BooksPost, OnlineStudyPost, OpenSourcePost, ProjectPost
from blog.models.blog_reply import (
    BlogPostReply,
    BooksPostReply,
    OnlineStudyPostReply,
    OpenSourcePostReply,
    ProjectPostReply,
)
from board.models.board import Notice, Reactivation, Visiter
from board.models.board_reply import NoticeReply, ReactivationReply, VisiterReply
from home.models.default import MainMenu, SiteInfo
from portfolio.models import PersonalInfo, WorkExperience
from users.models import User

pytestmark = [pytest.mark.django_db]

# (URL 이름공간, 게시판 이름, 글 모델, 댓글 모델, 댓글의 글 FK 이름, 글 생성 시 추가 필드)
BLOG_BOARDS = [
    ("blog", "project", ProjectPost, ProjectPostReply, "post", {"dev_lang": "python", "version": "1.0"}),
    ("blog", "online_study", OnlineStudyPost, OnlineStudyPostReply, "post", {"dev_lang": "python"}),
    ("blog", "blog", BlogPost, BlogPostReply, "post", {}),
    ("blog", "opensource", OpenSourcePost, OpenSourcePostReply, "post", {"dev_lang": "python"}),
    ("blog", "books", BooksPost, BooksPostReply, "post", {"dev_lang": "python"}),
]
BOARD_BOARDS = [
    ("board", "notice", Notice, NoticeReply, "board", {}),
    ("board", "visiter", Visiter, VisiterReply, "board", {}),
    ("board", "reactivation", Reactivation, ReactivationReply, "board", {}),
]
ALL_BOARDS = BLOG_BOARDS + BOARD_BOARDS
ALL_IDS = [b[1] for b in ALL_BOARDS]
BLOG_IDS = [b[1] for b in BLOG_BOARDS]
BOARD_IDS = [b[1] for b in BOARD_BOARDS]

SCAN_LIKE = ("iter_keys", "keys", "delete_pattern", "ttl")


def make_user(username, **extra):
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        nickname=username,
        password="password",
        verified=True,
        **extra,
    )


def logged_in(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def author():
    return make_user("author")


@pytest.fixture
def no_scan(monkeypatch):
    """요청 경로에서 키 공간 SCAN·TTL 조회를 쓰면 실패시킨다(INV-5)."""
    calls = []

    def forbid(name):
        def _forbidden(self, *args, **kwargs):
            calls.append(name)
            raise AssertionError(f"request path must not call cache.{name}")

        return _forbidden

    for name in SCAN_LIKE:
        monkeypatch.setattr(RedisCache, name, forbid(name))
    return calls


def detail_url(ns, name, pk):
    return reverse(f"{ns}:{name}_detail", kwargs={"pk": pk})


def reply_list_url(ns, name, pk, page="1"):
    url = reverse(f"{ns}:{name}_reply_list", kwargs={"pk": pk})
    return url if page is None else f"{url}?page={page}"


def make_post(post_model, author, extra, **fields):
    return post_model.objects.create(
        author=author, title=fields.pop("title", "t"), content="c", **extra, **fields
    )


def make_reply(reply_model, fk, post, author, comment="hi"):
    return reply_model.objects.create(author=author, comment=comment, **{fk: post})


# --- INV-5 (F-002·F-003): 요청 경로에 SCAN·TTL 없음 ---


@pytest.mark.parametrize("ns,name,post_model,reply_model,fk,extra", ALL_BOARDS, ids=ALL_IDS)
def test_detail_and_reply_list_never_scan(ns, name, post_model, reply_model, fk, extra, author, no_scan):
    post = make_post(post_model, author, extra)
    make_reply(reply_model, fk, post, author)
    client = Client()

    for _ in range(2):  # 미스, 히트
        assert client.get(detail_url(ns, name, post.pk)).status_code == 200
        assert client.get(reply_list_url(ns, name, post.pk)).status_code == 200

    assert no_scan == []


def test_portfolio_and_menu_never_scan(no_scan):
    # index("/")는 SQLite에서 렌더링할 수 없어 runserver 점검에서 확인한다(F-011).
    # 헤더의 메뉴·사이트 정보 태그도 이 요청들에서 함께 읽힌다.
    client = Client()

    for _ in range(2):
        for url in ["/portfolio/", "/portfolio/json/", "/blog/blog/"]:
            assert client.get(url).status_code == 200

    assert no_scan == []


# --- F-001 / D1-A: 삭제·숨김 글은 상세와 이웃 글에서 보이지 않는다 ---


@pytest.mark.parametrize("ns,name,post_model,reply_model,fk,extra", ALL_BOARDS, ids=ALL_IDS)
@pytest.mark.parametrize("state", ["is_deleted", "is_hidden"])
def test_deleted_or_hidden_post_detail_is_404(ns, name, post_model, reply_model, fk, extra, state, author):
    post = make_post(post_model, author, extra, **{state: True})

    assert Client().get(detail_url(ns, name, post.pk)).status_code == 404
    assert logged_in(author).get(detail_url(ns, name, post.pk)).status_code == 404


@pytest.mark.parametrize("ns,name,post_model,reply_model,fk,extra", BLOG_BOARDS, ids=BLOG_IDS)
def test_neighbor_links_skip_deleted_and_hidden_posts(ns, name, post_model, reply_model, fk, extra, author):
    first = make_post(post_model, author, extra, title="first")
    make_post(post_model, author, extra, title="deleted", is_deleted=True)
    middle = make_post(post_model, author, extra, title="middle")
    make_post(post_model, author, extra, title="hidden", is_hidden=True)
    last = make_post(post_model, author, extra, title="last")

    context = Client().get(detail_url(ns, name, middle.pk)).context

    assert context["pre_board"] == first
    assert context["next_board"] == last


@pytest.mark.parametrize("ns,name,post_model,reply_model,fk,extra", ALL_BOARDS, ids=ALL_IDS)
def test_detail_puts_no_queryset_in_the_cache(ns, name, post_model, reply_model, fk, extra, author):
    post = make_post(post_model, author, extra)
    Client().get(detail_url(ns, name, post.pk))

    for key in cache.keys("*"):
        assert not isinstance(cache.get(key), QuerySet), key


# --- F-008: 댓글 목록 page 값 ---


@pytest.mark.parametrize("ns,name,post_model,reply_model,fk,extra", ALL_BOARDS, ids=ALL_IDS)
@pytest.mark.parametrize("page", [None, "", "abc", "0", "-3", "999"])
def test_reply_list_accepts_any_page_value(ns, name, post_model, reply_model, fk, extra, page, author):
    post = make_post(post_model, author, extra)
    make_reply(reply_model, fk, post, author)

    response = Client().get(reply_list_url(ns, name, post.pk, page))

    assert response.status_code == 200
    assert response.json()[0] == {"number": 1, "num_pages": 1}
    assert response.json()[1]["comment"] == "hi"


@pytest.mark.parametrize("ns,name,post_model,reply_model,fk,extra", ALL_BOARDS, ids=ALL_IDS)
def test_reply_list_json_shape_is_unchanged(ns, name, post_model, reply_model, fk, extra, author):
    post = make_post(post_model, author, extra)
    make_reply(reply_model, fk, post, author)

    reply = Client().get(reply_list_url(ns, name, post.pk)).json()[1]

    assert set(reply) == {
        "pk", "author", "comment", "depth", "group", "parent", "post",
        "created_at", "thumbnail", "user_auth",
    }
    assert reply["post"] == str(post.pk)


# --- INV-6 (F-004·F-005): 쓰기 뒤 커밋되면 캐시가 바뀐다 ---


@pytest.mark.parametrize("ns,name,post_model,reply_model,fk,extra", ALL_BOARDS, ids=ALL_IDS)
def test_reply_list_refreshes_after_any_reply_write(
    ns, name, post_model, reply_model, fk, extra, author, django_capture_on_commit_callbacks
):
    post = make_post(post_model, author, extra)
    url = reply_list_url(ns, name, post.pk)
    client = Client()
    assert len(client.get(url).json()) == 1  # 페이지 정보만, 캐시됨

    with django_capture_on_commit_callbacks(execute=True):
        reply = make_reply(reply_model, fk, post, author, comment="first")
    assert [r["comment"] for r in client.get(url).json()[1:]] == ["first"]

    with django_capture_on_commit_callbacks(execute=True):
        reply.comment = "edited"
        reply.save()
    assert [r["comment"] for r in client.get(url).json()[1:]] == ["edited"]

    with django_capture_on_commit_callbacks(execute=True):
        reply.delete()
    assert client.get(url).json()[1:] == []


@pytest.mark.parametrize("ns,name,post_model,reply_model,fk,extra", ALL_BOARDS, ids=ALL_IDS)
def test_reply_cache_is_not_invalidated_before_commit(
    ns, name, post_model, reply_model, fk, extra, author, django_capture_on_commit_callbacks
):
    post = make_post(post_model, author, extra)
    url = reply_list_url(ns, name, post.pk)
    client = Client()
    client.get(url)

    with django_capture_on_commit_callbacks(execute=False) as callbacks:
        make_reply(reply_model, fk, post, author)
        # 커밋 전에는 아직 지우지 않는다: 지금 읽으면 옛 캐시
        assert len(client.get(url).json()) == 1

    assert callbacks  # 무효화는 커밋 뒤로 미뤄져 있다


# index 화면은 SQLite(테스트 DB)에서 렌더링할 수 없다(F-011: union + 조각 쿼리).
# 그래서 index는 캐시 키가 무효화되는지만 여기서 보고, 읽기 경로는 runserver(PostgreSQL)로 확인한다.
INDEX_KEY = "v2:index"


@pytest.mark.parametrize("action", ["set_delete", "set_hidden", "set_activate", "set_visible"])
def test_admin_bulk_action_invalidates_index(action, author, django_capture_on_commit_callbacks):
    post = BlogPost.objects.create(author=author, title="t", content="c")
    cache.set(INDEX_KEY, "stale")

    with django_capture_on_commit_callbacks(execute=True):
        getattr(_blog_admin(), action)(None, BlogPost.objects.filter(pk=post.pk))

    assert cache.get(INDEX_KEY) is None


def _blog_admin():
    from blog.admin.blog_admin import BlogPostAdmin

    return BlogPostAdmin(BlogPost, admin.site)


@pytest.mark.parametrize("ns,name,post_model,reply_model,fk,extra", BLOG_BOARDS, ids=BLOG_IDS)
def test_post_write_through_orm_invalidates_index_after_commit(
    ns, name, post_model, reply_model, fk, extra, author, django_capture_on_commit_callbacks
):
    cache.set(INDEX_KEY, "stale")
    with django_capture_on_commit_callbacks(execute=False) as callbacks:
        post = make_post(post_model, author, extra)
        assert cache.get(INDEX_KEY) == "stale"  # 커밋 전에는 지우지 않는다
    for callback in callbacks:
        callback()
    assert cache.get(INDEX_KEY) is None

    cache.set(INDEX_KEY, "stale")
    with django_capture_on_commit_callbacks(execute=True):
        post.delete()
    assert cache.get(INDEX_KEY) is None


@pytest.mark.parametrize("ns,name,post_model,reply_model,fk,extra", BLOG_BOARDS, ids=BLOG_IDS)
def test_opening_the_create_form_does_not_touch_the_cache(
    ns, name, post_model, reply_model, fk, extra, author, monkeypatch
):
    client = logged_in(author)
    deleted = []
    monkeypatch.setattr(RedisCache, "delete_pattern", lambda self, *a, **k: deleted.append(a))
    monkeypatch.setattr(RedisCache, "delete", lambda self, *a, **k: deleted.append(a))

    assert client.get(reverse(f"blog:{name}_create")).status_code == 200

    assert deleted == []


# --- F-006: 게시판 댓글 admin ---


@pytest.mark.parametrize("ns,name,post_model,reply_model,fk,extra", BOARD_BOARDS, ids=BOARD_IDS)
def test_board_reply_admin_save_and_delete_work_and_refresh_the_list(
    ns, name, post_model, reply_model, fk, extra, author, django_capture_on_commit_callbacks
):
    post = make_post(post_model, author, extra)
    reply = make_reply(reply_model, fk, post, author, comment="before")
    url = reply_list_url(ns, name, post.pk)
    client = Client()
    client.get(url)
    model_admin = admin.site._registry.get(reply_model) or _registered_admin(reply_model)

    with django_capture_on_commit_callbacks(execute=True):
        reply.comment = "after"
        model_admin.save_model(None, reply, None, True)
    assert client.get(url).json()[1]["comment"] == "after"

    with django_capture_on_commit_callbacks(execute=True):
        model_admin.delete_model(None, reply)
    assert client.get(url).json()[1:] == []


def _registered_admin(model):
    from board.admin import notice_admin, reactivation_admin, visiter_admin  # noqa: F401  등록 보장

    for site in _all_admin_sites():
        if model in site._registry:
            return site._registry[model]
    raise LookupError(model)


def _all_admin_sites():
    from django.contrib.admin.sites import all_sites

    return list(all_sites)


# --- F-007: portfolio 언어별 ---


def work_experience(lang, title):
    return WorkExperience.objects.create(
        language=lang,
        title=title,
        role="0",
        color="0",
        summary="s",
        content="c",
        project_start_date=datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc),
    )


def test_work_experience_json_follows_the_request_language():
    work_experience("0", "korean")
    work_experience("1", "english")
    client = Client()

    ko = client.get("/portfolio/json/", HTTP_ACCEPT_LANGUAGE="ko").json()
    en = client.get("/portfolio/json/", HTTP_ACCEPT_LANGUAGE="en").json()

    assert [w["title"] for w in ko] == ["korean"]
    assert [w["title"] for w in en] == ["english"]


@pytest.mark.parametrize("lang,accept", [("0", "ko"), ("1", "en")])
def test_portfolio_refreshes_for_every_language(lang, accept, django_capture_on_commit_callbacks):
    info = PersonalInfo.objects.create(language=lang, name="before", country="KR")
    client = Client()
    assert client.get("/portfolio/", HTTP_ACCEPT_LANGUAGE=accept).context["info"].name == "before"

    with django_capture_on_commit_callbacks(execute=True):
        info.name = "after"
        info.save()

    assert client.get("/portfolio/", HTTP_ACCEPT_LANGUAGE=accept).context["info"].name == "after"


# --- F-004: 메뉴·사이트 정보 ---


def menu_names():
    from home.templatetags.home_tag import main_menu_tag

    return [m.menu_name for m in main_menu_tag()]


def test_main_menu_refreshes_after_save_and_move(django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        a = MainMenu.objects.create(menu_name="a", menu_path="/a/")
        b = MainMenu.objects.create(menu_name="b", menu_path="/b/")
    assert menu_names() == ["a", "b"]

    with django_capture_on_commit_callbacks(execute=True):
        b.move_to(a, "left")
    assert menu_names() == ["b", "a"]

    with django_capture_on_commit_callbacks(execute=True):
        a.menu_name = "renamed"
        a.save()
    assert menu_names() == ["b", "renamed"]


def test_site_info_refreshes_after_save(django_capture_on_commit_callbacks):
    from home.templatetags.home_tag import site_info_tag

    with django_capture_on_commit_callbacks(execute=True):
        info = SiteInfo.objects.create()
    assert site_info_tag().pk == info.pk

    with django_capture_on_commit_callbacks(execute=True):
        info.delete()
    assert site_info_tag() is None


# --- INV-7: 요청자별 값은 캐시에 없다 ---


def _walk(value):
    yield value
    if isinstance(value, dict):
        for k, v in value.items():
            yield k
            yield from _walk(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from _walk(v)


@pytest.mark.parametrize("ns,name,post_model,reply_model,fk,extra", ALL_BOARDS, ids=ALL_IDS)
def test_cache_holds_no_visitor_values(ns, name, post_model, reply_model, fk, extra, author):
    post = make_post(post_model, author, extra)
    make_reply(reply_model, fk, post, author)
    client = logged_in(author)
    for url in [detail_url(ns, name, post.pk), reply_list_url(ns, name, post.pk), "/portfolio/"]:
        client.get(url)

    for key in cache.keys("*"):
        if "django.contrib.sessions" in key:
            continue
        for item in _walk(cache.get(key)):
            assert not isinstance(item, User), key
            assert item not in ("user_auth", "like_state", "get_in_touch_form"), key
