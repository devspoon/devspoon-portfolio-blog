"""2단계 템플릿 계약.

- 고정(characterization): 통합 전후로 같은 정보가 렌더링되어야 한다.
- 계약(contract): 승인된 구조 개선(ADR-003~007) — 단일 title/h1/main, 서버가 만든 정확한 링크.
"""

import pytest
from bs4 import BeautifulSoup
from django.urls import reverse

from blog.models.blog import BlogPost, BooksPost, OnlineStudyPost, OpenSourcePost, ProjectPost, Tag
from users.models import User

headers = {"HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0"}

# prefix, model, extra fields, strings the detail meta block must show, form heading, list title.
# List titles are the URL segments blog.js used to inject, kept so the pages look the same (C-2).
BLOG_TYPES = [
    ("project", ProjectPost, dict(dev_lang="python", version="1.2.3", repository="https://github.com/ex/repo"),
     ["python", "1.2.3", "github.com/ex/repo"], "Project", "project"),
    ("online_study", OnlineStudyPost, dict(dev_lang="python"), ["python"], "Online Study", "onlinestudy"),
    ("blog", BlogPost, {}, [], "Blog", "blog"),
    ("opensource", OpenSourcePost, dict(dev_lang="python", repository="https://github.com/ex/repo"),
     ["python"], "OpenSource", "opensource"),
    ("books", BooksPost, dict(dev_lang="python"), ["python"], "Books", "books"),
]
ids = [t[0] for t in BLOG_TYPES]


def soup(response):
    assert response.status_code == 200
    return BeautifulSoup(response.content.decode(), "html.parser")


@pytest.fixture
def staff(client):
    user = User.objects.create_user(username="author", password="password", is_staff=True)
    client.login(username="author", password="password")
    return user


@pytest.fixture
def posts(request, staff):
    prefix, model, extra, *_ = request.param
    tag = Tag.objects.create(tag="django")
    created = []
    for i in range(1, 4):
        p = model.objects.create(author=staff, title=f"title {i}", content=f"<p>body {i}</p>", **extra)
        p.tag_set.add(tag)
        created.append(p)
    return request.param, created


pytestmark = [pytest.mark.blog, pytest.mark.django_db]
param = pytest.mark.parametrize("posts", BLOG_TYPES, ids=ids, indirect=True)


# ---------- characterization (green before and after) ----------

@param
def test_list_shows_every_post(client, posts):
    (prefix, *_), items = posts
    page = soup(client.get(reverse(f"blog:{prefix}_list"), **headers))
    text = page.get_text()
    for p in items:
        assert p.title in text


@param
def test_detail_shows_content_meta_tags_and_owner_buttons(client, posts):
    (prefix, _, _, meta, _, _), items = posts
    p = items[1]
    page = soup(client.get(reverse(f"blog:{prefix}_detail", args=[p.pk]), **headers))
    text = page.get_text()
    assert p.title in text and "body 2" in text
    for value in meta:
        assert value in text
    assert page.find("a", string="django")
    assert page.find("a", href=reverse(f"blog:{prefix}_update", args=[p.pk]))
    form = page.find("form", action=reverse(f"blog:{prefix}_delete", args=[p.pk]))
    assert form and form.find("input", attrs={"name": "csrfmiddlewaretoken"})


@param
def test_create_and_update_forms_render_fields(client, posts):
    (prefix, *_), items = posts
    for url in (reverse(f"blog:{prefix}_create"), reverse(f"blog:{prefix}_update", args=[items[0].pk])):
        page = soup(client.get(url, **headers))
        form = page.find("form", attrs={"enctype": "multipart/form-data"})
        assert form.find("input", attrs={"name": "csrfmiddlewaretoken"})
        assert form.find(attrs={"name": "title"})
        assert form.find(attrs={"name": "content"}) or form.find("iframe")  # summernote
        assert all(f.get("title") for f in page.find_all("iframe"))  # axe frame-title
        assert form.find("button")
        assert 'value="None"' not in str(form)


# ---------- contract (red before ADR-003~007, green after) ----------

@param
def test_list_title_heading_and_links_are_server_rendered(client, posts):
    (prefix, _, _, _, _, list_title), items = posts
    page = soup(client.get(reverse(f"blog:{prefix}_list"), **headers))
    assert len(page.find_all("title")) == 1
    assert list_title in page.title.get_text()
    assert len(page.find_all("h1")) == 1 and list_title in page.h1.get_text()
    assert len(page.find_all("main")) == 1
    for p in items:
        assert page.find("a", href=reverse(f"blog:{prefix}_detail", args=[p.pk]))
    assert page.find("a", href=reverse(f"blog:{prefix}_create"))


@param
def test_detail_prev_next_links_point_to_neighbours(client, posts):
    (prefix, *_), (older, current, newer) = posts
    page = soup(client.get(reverse(f"blog:{prefix}_detail", args=[current.pk]), **headers))
    assert len(page.find_all("title")) == 1 and len(page.find_all("h1")) == 1
    assert page.find("article")
    assert page.find("a", href=reverse(f"blog:{prefix}_detail", args=[older.pk]), id="nav-left")
    assert page.find("a", href=reverse(f"blog:{prefix}_detail", args=[newer.pk]), id="nav-right")


@param
def test_update_form_heading_and_cancel_link(client, posts):
    (prefix, _, _, _, heading, _), items = posts
    page = soup(client.get(reverse(f"blog:{prefix}_update", args=[items[0].pk]), **headers))
    assert page.find("main").h1.get_text() == heading
    cancel = page.find("a", string="Cancel")
    assert cancel["href"] == reverse(f"blog:{prefix}_detail", args=[items[0].pk])
    page = soup(client.get(reverse(f"blog:{prefix}_create"), **headers))
    assert page.find("a", string="Cancel")["href"] == reverse(f"blog:{prefix}_list")
