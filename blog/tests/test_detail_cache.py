"""ADR-017: detail pages must compute viewer-specific state per request, never from the per-post cache."""

import pytest
from django.test import Client
from django.urls import reverse

from blog.models.blog import BlogPost, ProjectPost
from board.models import Notice
from users.models import User

headers = {"HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0"}
CASES = [("blog:blog", BlogPost), ("blog:project", ProjectPost), ("board:notice", Notice)]


@pytest.fixture
def author():
    return User.objects.create_user(username="author", email="author@example.com", nickname="author", password="password", is_staff=True)


def client_for(user=None):
    c = Client(**headers)
    if user:
        c.force_login(user)
    return c


@pytest.mark.django_db
@pytest.mark.parametrize("prefix,model", CASES, ids=[c[0] for c in CASES])
def test_owner_buttons_only_for_author_even_after_cache(author, prefix, model):
    post = model.objects.create(author=author, title="t", content="<p>c</p>")
    url = reverse(f"{prefix}_detail", args=[post.pk])
    edit_url = reverse(f"{prefix}_update", args=[post.pk])

    assert edit_url in client_for(author).get(url).content.decode()      # author's visit fills the cache
    assert edit_url not in client_for().get(url).content.decode()        # anonymous visitor
    other = User.objects.create_user(username="other", email="other@example.com", nickname="other", password="password")
    assert edit_url not in client_for(other).get(url).content.decode()   # another member


REPLY_CASES = [("blog:blog", BlogPost), ("blog:project", ProjectPost), ("board:notice", Notice)]


@pytest.mark.django_db
@pytest.mark.parametrize("prefix,model", REPLY_CASES, ids=[c[0] for c in REPLY_CASES])
def test_reply_list_is_viewer_neutral(author, prefix, model):
    """The reply page is cached per post+page; user_auth is added per request and author ids stay hidden."""
    post = model.objects.create(author=author, title="t", content="<p>c</p>")
    client_for(author).post(reverse(f"{prefix}_reply_create", args=[post.pk]), {"comment": "hi", "depth": 0, "parent": ""})
    url = reverse(f"{prefix}_reply_list", args=[post.pk])

    first = client_for(author).get(url).json()[1]         # the author's request fills the cache
    second = client_for().get(url).json()[1]              # an anonymous visitor reads the same cache
    assert first["user_auth"] is True and second["user_auth"] is False
    assert "author_id" not in first and "author_id" not in second


@pytest.mark.django_db
def test_like_state_is_per_viewer(author):
    post = BlogPost.objects.create(author=author, title="t", content="<p>c</p>")
    post.like_user_set.add(author)
    url = reverse("blog:blog_detail", args=[post.pk])
    assert 'aria-pressed="true"' in client_for(author).get(url).content.decode()
    other = User.objects.create_user(username="other", email="other@example.com", nickname="other", password="password")
    assert 'aria-pressed="false"' in client_for(other).get(url).content.decode()
