"""phase5 ADR-001: 상태 변경 요청과 캐시 재생성은 replica가 늦어도 primary(default)에서 읽는다.

replica1은 테스트에서 행이 없는 별도 DB다. 그 DB에서 읽으면 "아직 복제되지 않은" 상태를 본다.
"""

import pytest
from django.db import router
from django.test import Client
from django.urls import reverse

from blog.models.blog import BlogPost
from blog.models.blog_reply import BlogPostReply
from common.components.django_redis_cache_components import cached
from common.core.replica_router import ReplicationRouter
from users.models import User

both = pytest.mark.django_db(databases=["default", "replica1"])
headers = {"HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0"}


@pytest.fixture
def stale_replica(monkeypatch):
    monkeypatch.setattr(router, "routers", [ReplicationRouter()])


@pytest.fixture
def author():
    return User.objects.create_user(username="author", email="author@example.com", nickname="author", password="password")


def client_for(user=None):
    c = Client(**headers)
    if user:
        c.force_login(user)
    return c


@both
def test_plain_reads_still_go_to_the_replica(stale_replica, author):
    post = BlogPost.objects.create(author=author, title="t", content="<p>c</p>")
    assert router.db_for_read(BlogPost) == "replica1"
    assert client_for().get(reverse("blog:blog_detail", args=[post.pk])).status_code == 404  # 아직 복제 전


@both
def test_cache_build_reads_the_primary(stale_replica, author):
    BlogPost.objects.create(author=author, title="t", content="<p>c</p>")
    assert len(cached("phase5:test", lambda: list(BlogPost.objects.all()))) == 1


@both
def test_reply_list_cache_is_built_from_the_primary(stale_replica, author):
    post = BlogPost.objects.create(author=author, title="t", content="<p>c</p>")
    BlogPostReply.objects.create(author=author, post=post, comment="hi")
    body = client_for().get(reverse("blog:blog_reply_list", args=[post.pk]), {"page": 1}).json()
    assert [r["comment"] for r in body[1:]] == ["hi"]


@both
def test_reply_create_reads_the_primary_inside_the_request(author, monkeypatch):
    post = BlogPost.objects.create(author=author, title="t", content="<p>c</p>")
    # 로그인은 라우터를 켜기 전에: 로그인 때 도는 사용자 저장 시그널의 replica 읽기는 이 단계 범위 밖(ledger F-005)
    c = client_for(author)
    monkeypatch.setattr(router, "routers", [ReplicationRouter()])
    url = reverse("blog:blog_reply_create", args=[post.pk])
    assert c.post(url, {"comment": "one", "depth": 0, "parent": ""}).status_code == 302
    assert c.post(url, {"comment": "two", "depth": 0, "parent": ""}).status_code == 302
    first, second = BlogPostReply.objects.using("default").order_by("pk")
    assert (first.group, second.group) == (1, 2)  # 커밋 전 값을 replica에서 읽으면 어긋난다
    # 대댓글: 부모 조회도 primary에서
    assert c.post(url, {"comment": "child", "depth": 1, "parent": first.pk}).status_code == 302
    child = BlogPostReply.objects.using("default").get(comment="child")
    assert (child.parent_id, child.group, child.depth) == (first.pk, 1, 1)
