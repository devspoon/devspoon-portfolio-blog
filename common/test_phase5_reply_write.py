"""phase5 ADR-003~005: 댓글 생성·수정은 조작된 입력에 500이나 잘못된 행을 만들지 않는다. 8개 게시판 모두."""

import json

import pytest
from django.test import Client
from django.urls import reverse

from blog.models.blog_reply import (
    BlogPostReply,
    BooksPostReply,
    OnlineStudyPostReply,
    OpenSourcePostReply,
    ProjectPostReply,
)
from board.models.board_reply import NoticeReply, ReactivationReply, VisiterReply
from users.models import User

headers = {"HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0"}
CASES = [
    ("blog:blog", BlogPostReply),
    ("blog:project", ProjectPostReply),
    ("blog:online_study", OnlineStudyPostReply),
    ("blog:opensource", OpenSourcePostReply),
    ("blog:books", BooksPostReply),
    ("board:notice", NoticeReply),
    ("board:visiter", VisiterReply),
    ("board:reactivation", ReactivationReply),
]
board_cases = pytest.mark.parametrize("prefix,reply_model", CASES, ids=[c[0] for c in CASES])


def fk_of(reply_model):
    return "board" if hasattr(reply_model, "board_id") else "post"


def make_post(reply_model, author, **extra):
    post_model = reply_model._meta.get_field(fk_of(reply_model)).related_model
    return post_model.objects.create(author=author, title="t", content="<p>c</p>", **extra)


def make_reply(reply_model, post, author, **extra):
    return reply_model.objects.create(author=author, comment="parent", **{fk_of(reply_model): post}, **extra)


@pytest.fixture
def author():
    return User.objects.create_user(username="author", email="author@example.com", nickname="author", password="password")


@pytest.fixture
def client(author):
    c = Client(**headers)
    c.force_login(author)
    return c


def create(client, prefix, post, **data):
    payload = {"comment": "hi", "depth": 0, "parent": ""} | data
    return client.post(reverse(f"{prefix}_reply_create", args=[post.pk]), payload)


def refreshed_count(post):
    post.refresh_from_db()
    return post.reply_count


# --- 생성 -------------------------------------------------------------------------------------


@pytest.mark.django_db
@board_cases
@pytest.mark.parametrize("parent", ["999999", "abc"])
def test_unknown_parent_is_rejected(client, author, prefix, reply_model, parent):
    post = make_post(reply_model, author)
    assert create(client, prefix, post, parent=parent).status_code == 400
    assert reply_model.objects.count() == 0 and refreshed_count(post) == 0


@pytest.mark.django_db
@board_cases
def test_parent_from_another_post_is_rejected(client, author, prefix, reply_model):
    post, other = make_post(reply_model, author), make_post(reply_model, author)
    foreign = make_reply(reply_model, other, author)
    assert create(client, prefix, post, parent=foreign.pk).status_code == 400
    assert reply_model.objects.count() == 1 and refreshed_count(post) == 0


@pytest.mark.django_db
@board_cases
def test_depth_is_computed_by_the_server(client, author, prefix, reply_model):
    post = make_post(reply_model, author)
    assert create(client, prefix, post, depth=7).status_code == 302
    top = reply_model.objects.get()
    assert top.depth == 0 and top.parent_id is None
    deep = make_reply(reply_model, post, author, depth=3, group=top.group, parent=top)
    assert create(client, prefix, post, comment="cap", depth=99, parent=deep.pk).status_code == 302
    capped = reply_model.objects.get(comment="cap")
    assert (capped.depth, capped.group, capped.parent_id) == (3, top.group, deep.pk)  # JS MAX_DEPTH와 같다


@pytest.mark.django_db
@board_cases
@pytest.mark.parametrize("state", [{"is_deleted": True}, {"is_hidden": True}])
def test_inactive_post_cannot_get_replies(client, author, prefix, reply_model, state):
    post = make_post(reply_model, author, **state)
    assert create(client, prefix, post).status_code == 404
    assert reply_model.objects.count() == 0 and refreshed_count(post) == 0


@pytest.mark.django_db
@board_cases
@pytest.mark.parametrize("comment,status", [("   ", 302), ("x" * 3001, 400)])
def test_blank_or_too_long_comment_is_not_saved(client, author, prefix, reply_model, comment, status):
    post = make_post(reply_model, author)
    assert create(client, prefix, post, comment=comment).status_code == status
    assert reply_model.objects.count() == 0 and refreshed_count(post) == 0


@pytest.mark.django_db
@board_cases
def test_valid_reply_still_redirects_and_counts(client, author, prefix, reply_model):
    post = make_post(reply_model, author)
    response = create(client, prefix, post, comment="x" * 3000)
    assert response.status_code == 302 and response.url == reverse(f"{prefix}_detail", args=[post.pk])
    assert reply_model.objects.get().group == 1 and refreshed_count(post) == 1


# --- 수정 -------------------------------------------------------------------------------------


def update(client, prefix, post, reply, body):
    url = reverse(f"{prefix}_reply_update", args=[post.pk, reply.pk])
    return client.post(url, body if isinstance(body, str) else json.dumps(body), content_type="application/json")


@pytest.mark.django_db
@board_cases
@pytest.mark.parametrize("body", ["not json", "[1]", {}, {"comment": 5}, {"comment": "  "}, {"comment": "x" * 3001}])
def test_bad_update_is_rejected(client, author, prefix, reply_model, body):
    post = make_post(reply_model, author)
    reply = make_reply(reply_model, post, author)
    assert update(client, prefix, post, reply, body).status_code == 400
    reply.refresh_from_db()
    assert reply.comment == "parent"


@pytest.mark.django_db
@board_cases
def test_update_through_another_post_url_is_not_found(client, author, prefix, reply_model):
    post, other = make_post(reply_model, author), make_post(reply_model, author)
    reply = make_reply(reply_model, post, author)
    assert update(client, prefix, other, reply, {"comment": "new"}).status_code == 404


@pytest.mark.django_db
@board_cases
def test_valid_update_keeps_the_json_contract(client, author, prefix, reply_model):
    post = make_post(reply_model, author)
    reply = make_reply(reply_model, post, author)
    assert update(client, prefix, post, reply, {"comment": "new"}).json() == {"message": "Reply updated"}
    assert update(client, prefix, post, reply, {"comment": None}).json() == {"message": "Reply note updated"}
    reply.refresh_from_db()
    assert reply.comment == "new"
    other = User.objects.create_user(username="o", email="o@example.com", nickname="o", password="password")
    c = Client(**headers)
    c.force_login(other)
    assert update(c, prefix, post, reply, {"comment": "x"}).status_code == 403
