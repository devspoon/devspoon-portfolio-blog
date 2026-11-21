"""Tag search: heading shows the tag text, results are paged (10 per page)."""
from unittest import mock

import pytest
from bs4 import BeautifulSoup
from django.urls import reverse

from blog.models.blog import BlogPost, Tag
from home.views.service.search import Search
from users.models import User

FIELDS = ("pk", "title", "created_at", "author__username", "visit_count", "table_name")


def sqlite_tag_query(self, instance, tag):
    # the real query adds ordering/distinct that SQLite refuses inside UNION; the union and paging stay real
    return instance.objects.filter(tag_set__in=tag).order_by().values(*FIELDS)


@pytest.mark.django_db
def test_tag_search_shows_tag_text_and_pages_results(client):
    author = User.objects.create_user(username="author", password="password")
    tag = Tag.objects.create(tag="django")
    for i in range(12):
        BlogPost.objects.create(author=author, title=f"post {i}", content="<p>c</p>").tag_set.add(tag)
    url = reverse("home:search_queryset")
    with mock.patch.object(Search, "get_tag_search_query_set", sqlite_tag_query):
        first = client.get(url, {"tag": "django"}, HTTP_USER_AGENT="Mozilla/5.0 Chrome/112.0")
        second = client.get(url, {"tag": "django", "page": 2}, HTTP_USER_AGENT="Mozilla/5.0 Chrome/112.0")
    assert first.context["tag"] == "django"
    h1 = BeautifulSoup(first.content, "html.parser").h1.get_text()
    assert "django" in h1 and "QuerySet" not in h1
    assert len(first.context["board"]) == 10 and len(second.context["board"]) == 2
    assert 'href="?page=2&amp;tag=django"' in first.content.decode()
    page = BeautifulSoup(first.content, "html.parser")
    summary = page.select_one(".search-results__summary").get_text()
    assert "django" in summary and "12 results" in summary
    items = page.select(".search-results__list .search-item")
    assert len(items) == 10
    # detail URLs per board type are covered by blog/tests/test_phase4_data_integrity.py (real query)
    for item in items:
        assert len(item.find_all("a")) == 1 and item.select_one("h2.search-item__title a")["href"]
        assert item.select_one(".search-item__kind").get_text(strip=True)
        assert "author" not in item.get_text()  # the login name is never shown
