"""1단계 보안 계약: 상태 변경은 POST 전용, 작성은 staff 전용, 본문 HTML은 정제 후 출력."""

import pytest
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

headers = {"HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0"}

BLOG_TYPES = [
    ("blog", BlogPost, BlogPostReply),
    ("books", BooksPost, BooksPostReply),
    ("online_study", OnlineStudyPost, OnlineStudyPostReply),
    ("opensource", OpenSourcePost, OpenSourcePostReply),
    ("project", ProjectPost, ProjectPostReply),
]
ids = [t[0] for t in BLOG_TYPES]

XSS = (
    '<script>alert("x")</script>'
    '<p onclick="steal()">safe text</p>'
    '<img src="x" onerror="steal()">'
    '<a href="javascript:steal()">link</a>'
)


@pytest.fixture
def author(client):
    user = User.objects.create_user(username="author", password="password", is_staff=True)
    client.login(username="author", password="password")
    return user


def make_post(model, author, content="<p>hello</p>"):
    return model.objects.create(author=author, title="t", content=content)


@pytest.mark.blog
@pytest.mark.django_db
@pytest.mark.parametrize("prefix,model,reply_model", BLOG_TYPES, ids=ids)
class TestBlogStateChangeIsPostOnly:
    def test_delete_get_is_405_and_keeps_post(self, client, author, prefix, model, reply_model):
        post = make_post(model, author)
        response = client.get(reverse(f"blog:{prefix}_delete", args=[post.pk]), **headers)
        assert response.status_code == 405
        post.refresh_from_db()
        assert post.is_deleted is False

    def test_delete_post_by_author_soft_deletes(self, client, author, prefix, model, reply_model):
        post = make_post(model, author)
        response = client.post(reverse(f"blog:{prefix}_delete", args=[post.pk]), **headers)
        assert response.status_code == 302
        post.refresh_from_db()
        assert post.is_deleted is True

    def test_reply_delete_get_is_405(self, client, author, prefix, model, reply_model):
        post = make_post(model, author)
        reply = reply_model.objects.create(post=post, author=author, comment="c")
        url = reverse(f"blog:{prefix}_reply_delete", args=[post.pk, reply.pk])
        assert client.get(url, **headers).status_code == 405
        assert reply_model.objects.filter(pk=reply.pk).exists()

    def test_reply_delete_post_by_author(self, client, author, prefix, model, reply_model):
        post = make_post(model, author)
        reply = reply_model.objects.create(post=post, author=author, comment="c")
        url = reverse(f"blog:{prefix}_reply_delete", args=[post.pk, reply.pk])
        assert client.post(url, **headers).status_code == 302
        assert not reply_model.objects.filter(pk=reply.pk).exists()

    def test_like_get_is_405(self, client, author, prefix, model, reply_model):
        post = make_post(model, author)
        assert client.get(reverse(f"blog:{prefix}_like", args=[post.pk]), **headers).status_code == 405

    def test_like_post_toggles(self, client, author, prefix, model, reply_model):
        post = make_post(model, author)
        response = client.post(reverse(f"blog:{prefix}_like", args=[post.pk]), **headers)
        assert response.status_code == 200
        assert response.json()["like_count"] == 1


@pytest.mark.blog
@pytest.mark.django_db
@pytest.mark.parametrize("prefix", ids)
def test_create_is_staff_only(user, prefix):
    # `user` fixture = 로그인한 일반 회원
    assert user.get(reverse(f"blog:{prefix}_create"), **headers).status_code == 403


@pytest.mark.blog
@pytest.mark.django_db
@pytest.mark.parametrize("prefix", ids)
def test_create_anonymous_redirects_to_login(client, prefix):
    response = client.get(reverse(f"blog:{prefix}_create"), **headers)
    assert response.status_code == 302
    assert reverse("users:login") in response.url


@pytest.mark.blog
@pytest.mark.django_db
@pytest.mark.parametrize("prefix,model,reply_model", BLOG_TYPES, ids=ids)
def test_detail_sanitizes_content(client, author, prefix, model, reply_model):
    post = make_post(model, author, content=XSS)
    response = client.get(reverse(f"blog:{prefix}_detail", args=[post.pk]), **headers)
    assert response.status_code == 200
    html = response.content.decode()
    assert "safe text" in html
    for bad in ('alert("x")', "steal()", "javascript:"):
        assert bad not in html


@pytest.mark.blog
@pytest.mark.django_db
@pytest.mark.parametrize("prefix", ids)
def test_list_renders(client, prefix):
    assert client.get(reverse(f"blog:{prefix}_list"), **headers).status_code == 200
