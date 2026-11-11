"""1단계 보안 계약(게시판): 상태 변경은 POST 전용, 공지 작성은 staff 전용, 본문 HTML은 정제 후 출력."""

import pytest
from django.urls import reverse

from board.models import (
    Notice,
    NoticeReply,
    Reactivation,
    ReactivationReply,
    Visiter,
    VisiterReply,
)
from users.models import User

headers = {"HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0"}

BOARD_TYPES = [
    ("notice", Notice, NoticeReply),
    ("reactivation", Reactivation, ReactivationReply),
    ("visiter", Visiter, VisiterReply),
]
ids = [t[0] for t in BOARD_TYPES]

XSS = '<script>alert("x")</script><p onclick="steal()">safe text</p><img src="x" onerror="steal()">'


@pytest.fixture
def author(client):
    user = User.objects.create_user(username="author", password="password", is_staff=True)
    client.login(username="author", password="password")
    return user


def make_post(model, author, content="<p>hello</p>"):
    return model.objects.create(author=author, title="t", content=content)


@pytest.mark.board
@pytest.mark.django_db
@pytest.mark.parametrize("prefix,model,reply_model", BOARD_TYPES, ids=ids)
class TestBoardStateChangeIsPostOnly:
    def test_delete_get_is_405_and_keeps_post(self, client, author, prefix, model, reply_model):
        post = make_post(model, author)
        assert client.get(reverse(f"board:{prefix}_delete", args=[post.pk]), **headers).status_code == 405
        post.refresh_from_db()
        assert post.is_deleted is False

    def test_delete_post_by_author_soft_deletes(self, client, author, prefix, model, reply_model):
        post = make_post(model, author)
        assert client.post(reverse(f"board:{prefix}_delete", args=[post.pk]), **headers).status_code == 302
        post.refresh_from_db()
        assert post.is_deleted is True

    def test_reply_delete_get_is_405(self, client, author, prefix, model, reply_model):
        post = make_post(model, author)
        reply = reply_model.objects.create(board=post, author=author, comment="c")
        url = reverse(f"board:{prefix}_reply_delete", args=[post.pk, reply.pk])
        assert client.get(url, **headers).status_code == 405
        assert reply_model.objects.filter(pk=reply.pk).exists()

    def test_reply_delete_post_by_author(self, client, author, prefix, model, reply_model):
        post = make_post(model, author)
        reply = reply_model.objects.create(board=post, author=author, comment="c")
        url = reverse(f"board:{prefix}_reply_delete", args=[post.pk, reply.pk])
        assert client.post(url, **headers).status_code == 302
        assert not reply_model.objects.filter(pk=reply.pk).exists()


@pytest.mark.board
@pytest.mark.django_db
@pytest.mark.parametrize("prefix,expected", [("notice", 403), ("reactivation", 200), ("visiter", 200)])
def test_create_permission(user, prefix, expected):
    # `user` fixture = 로그인한 일반 회원. 공지만 staff 전용
    assert user.get(reverse(f"board:{prefix}_create"), **headers).status_code == expected


@pytest.mark.board
@pytest.mark.django_db
@pytest.mark.parametrize("prefix,model,reply_model", BOARD_TYPES, ids=ids)
def test_detail_sanitizes_content(client, author, prefix, model, reply_model):
    post = make_post(model, author, content=XSS)
    response = client.get(reverse(f"board:{prefix}_detail", args=[post.pk]), **headers)
    assert response.status_code == 200
    html = response.content.decode()
    assert "safe text" in html
    assert 'alert("x")' not in html
    assert "steal()" not in html


@pytest.mark.board
@pytest.mark.django_db
@pytest.mark.parametrize("prefix", ids)
def test_list_renders(client, prefix):
    assert client.get(reverse(f"board:{prefix}_list"), **headers).status_code == 200
