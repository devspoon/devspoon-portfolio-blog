"""1단계 핫픽스 회귀 테스트 (docs/crp/groups/phase1-hotfix).

블로그 게시판 5종이 같은 코드를 복사해 쓰므로 모두 parametrize 한다.
"""
import pytest
from django.core.cache import cache
from django.test import Client
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
