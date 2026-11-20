"""1단계 핫픽스 회귀 테스트.

블로그 게시판 5종이 같은 코드를 복사해 쓰므로 모두 parametrize 한다.
"""
import pytest
from django.core.cache import cache
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from blog.models.blog import (
    BlogPost,
    BooksPost,
    OnlineStudyPost,
    OpenSourcePost,
    ProjectPost,
)
from blog.models.blog_reply import (
    BlogPostReply,
    BooksPostReply,
    OnlineStudyPostReply,
    OpenSourcePostReply,
    ProjectPostReply,
)
from users.models import User

pytestmark = [pytest.mark.blog, pytest.mark.django_db]

# (게시판 이름, 글 모델, 댓글 모델, 글 생성 시 필요한 추가 필드)
BOARDS = [
    ("project", ProjectPost, ProjectPostReply, {"dev_lang": "python", "version": "1.0"}),
    ("online_study", OnlineStudyPost, OnlineStudyPostReply, {"dev_lang": "python"}),
    ("blog", BlogPost, BlogPostReply, {}),
    ("opensource", OpenSourcePost, OpenSourcePostReply, {"dev_lang": "python"}),
    ("books", BooksPost, BooksPostReply, {"dev_lang": "python"}),
]
BOARD_IDS = [board[0] for board in BOARDS]


def make_user(username):
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        nickname=username,
        password="password",
        verified=True,
    )


def logged_in(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def author():
    return make_user("author")


@pytest.fixture
def other():
    return make_user("other")


# --- C2: 댓글 삭제가 롤백되지 않고 reply_count가 줄어든다 (F-004, INV-4) ---


@pytest.mark.parametrize("name,post_model,reply_model,extra", BOARDS, ids=BOARD_IDS)
def test_deleting_a_reply_removes_it_and_decrements_reply_count(
    name, post_model, reply_model, extra, author
):
    post = post_model.objects.create(
        author=author, title="t", content="c", reply_count=1, **extra
    )
    reply = reply_model.objects.create(author=author, comment="hi", post=post)

    reply.delete()

    assert not reply_model.objects.filter(pk=reply.pk).exists()
    post.refresh_from_db()
    assert post.reply_count == 0


@pytest.mark.parametrize("name,post_model,reply_model,extra", BOARDS, ids=BOARD_IDS)
def test_reply_count_never_goes_below_zero(name, post_model, reply_model, extra, author):
    post = post_model.objects.create(
        author=author, title="t", content="c", reply_count=0, **extra
    )
    reply = reply_model.objects.create(author=author, comment="hi", post=post)

    reply.delete()

    post.refresh_from_db()
    assert post.reply_count == 0


# --- C1: 상세 페이지의 요청자별 값은 요청자 기준이다 (F-001·F-002, INV-1~3) ---


@pytest.mark.parametrize("name,post_model,reply_model,extra", BOARDS, ids=BOARD_IDS)
def test_detail_owner_controls_follow_the_visitor_not_the_first_visitor(
    name, post_model, reply_model, extra, author, other
):
    post = post_model.objects.create(author=author, title="t", content="c", **extra)
    url = reverse(f"blog:{name}_detail", kwargs={"pk": post.pk})
    author_client = logged_in(author)

    # 작성자가 먼저 방문해 캐시를 채운다.
    assert author_client.get(url).context["user_auth"] is True

    assert logged_in(other).get(url).context["user_auth"] is False
    assert Client().get(url).context["user_auth"] is False
    assert author_client.get(url).context["user_auth"] is True


@pytest.mark.parametrize("name,post_model,reply_model,extra", BOARDS, ids=BOARD_IDS)
def test_detail_like_state_follows_the_visitor(
    name, post_model, reply_model, extra, author, other
):
    post = post_model.objects.create(author=author, title="t", content="c", **extra)
    post.like_user_set.add(author)
    url = reverse(f"blog:{name}_detail", kwargs={"pk": post.pk})

    assert logged_in(author).get(url).context["like_state"] is True
    assert logged_in(other).get(url).context["like_state"] is False
    assert Client().get(url).context["like_state"] is False


@pytest.mark.parametrize("name,post_model,reply_model,extra", BOARDS, ids=BOARD_IDS)
def test_detail_does_not_cache_visitor_values(
    name, post_model, reply_model, extra, author, other
):
    post = post_model.objects.create(author=author, title="t", content="c", **extra)
    url = reverse(f"blog:{name}_detail", kwargs={"pk": post.pk})

    logged_in(author).get(url)
    logged_in(other).get(url)

    assert cache.keys("*user_auth*") == []
    assert cache.keys("*like_state*") == []


# --- C1(댓글)·N1: 댓글 목록 (F-003·F-006·F-009, INV-1·INV-5, ADR-006) ---


def reply_list_url(name, post):
    # 화면 JS(static/js/modules/comments.js)는 항상 ?page=를 붙여 호출한다.
    return reverse(f"blog:{name}_reply_list", kwargs={"pk": post.pk}) + "?page=1"


@pytest.mark.parametrize("name,post_model,reply_model,extra", BOARDS, ids=BOARD_IDS)
def test_reply_list_owner_flag_follows_the_visitor(
    name, post_model, reply_model, extra, author, other
):
    post = post_model.objects.create(author=author, title="t", content="c", **extra)
    reply_model.objects.create(author=author, comment="hi", post=post)
    url = reply_list_url(name, post)

    # 작성자가 먼저 불러 캐시를 채운다. 응답의 0번은 페이지 정보다.
    assert logged_in(author).get(url).json()[1]["user_auth"] is True

    assert logged_in(other).get(url).json()[1]["user_auth"] is False
    assert Client().get(url).json()[1]["user_auth"] is False


@pytest.mark.parametrize("name,post_model,reply_model,extra", BOARDS, ids=BOARD_IDS)
def test_reply_list_owner_flag_does_not_depend_on_nickname(
    name, post_model, reply_model, extra
):
    # User.__str__은 nickname이다. nickname이 username과 달라도 작성자로 판정해야 한다.
    author = User.objects.create_user(
        username="author-login",
        email="author-login@example.com",
        nickname="Author Nick",
        password="password",
        verified=True,
    )
    post = post_model.objects.create(author=author, title="t", content="c", **extra)
    reply_model.objects.create(author=author, comment="hi", post=post)

    reply = logged_in(author).get(reply_list_url(name, post)).json()[1]

    assert reply["user_auth"] is True
    # 판정용 내부 값은 응답에 노출하지 않는다.
    assert "author_id" not in reply


def count_queries(client, url):
    with CaptureQueriesContext(connection) as queries:
        response = client.get(url)
    assert response.status_code == 200
    # 테스트 설정에서 켜진 django-silk가 확률적으로 자기 테이블을 정리하는 쿼리는 뺀다.
    return sum(
        1
        for query in queries.captured_queries
        if "silk_" not in query["sql"] and "SAVEPOINT" not in query["sql"]
    )


@pytest.mark.parametrize("name,post_model,reply_model,extra", BOARDS, ids=BOARD_IDS)
def test_reply_list_query_count_does_not_grow_with_replies(
    name, post_model, reply_model, extra, author
):
    def post_with_replies(count):
        post = post_model.objects.create(author=author, title="t", content="c", **extra)
        for _ in range(count):
            reply_model.objects.create(author=author, comment="hi", post=post)
        return reply_list_url(name, post)

    client = Client()
    # 첫 요청은 일자별 통계 row를 만드는 INSERT가 섞이므로 제외한다.
    count_queries(client, post_with_replies(0))

    assert count_queries(client, post_with_replies(1)) == count_queries(
        client, post_with_replies(5)
    )
