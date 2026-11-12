"""2단계 템플릿 계약(게시판). 구분은 blog/tests/test_templates.py 와 같다."""

import pytest
from bs4 import BeautifulSoup
from django.urls import reverse

from board.models import Notice, Reactivation, Visiter
from users.models import User

headers = {"HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0"}

# list title = the URL segment blog.js used to inject, kept so the pages look the same (C-2)
BOARD_TYPES = [("notice", Notice, "notice"), ("visiter", Visiter, "visiter"), ("reactivation", Reactivation, "reactivation")]
ids = [t[0] for t in BOARD_TYPES]


def soup(response):
    assert response.status_code == 200
    return BeautifulSoup(response.content.decode(), "html.parser")


@pytest.fixture
def posts(request, client):
    prefix, model, _ = request.param
    staff = User.objects.create_user(username="author", password="password", is_staff=True)
    client.login(username="author", password="password")
    return request.param, [model.objects.create(author=staff, title=f"title {i}", content=f"<p>body {i}</p>") for i in range(1, 4)]


pytestmark = [pytest.mark.board, pytest.mark.django_db]
param = pytest.mark.parametrize("posts", BOARD_TYPES, ids=ids, indirect=True)


# ---------- characterization ----------

@param
def test_list_shows_every_post(client, posts):
    (prefix, *_), items = posts
    text = soup(client.get(reverse(f"board:{prefix}_list"), **headers)).get_text()
    for p in items:
        assert p.title in text


@param
def test_detail_shows_content_and_owner_buttons(client, posts):
    (prefix, *_), items = posts
    p = items[1]
    page = soup(client.get(reverse(f"board:{prefix}_detail", args=[p.pk]), **headers))
    assert p.title in page.get_text() and "body 2" in page.get_text()
    assert page.find("a", href=reverse(f"board:{prefix}_update", args=[p.pk]))
    assert page.find("form", action=reverse(f"board:{prefix}_delete", args=[p.pk]))


@param
def test_create_and_update_forms_render_fields(client, posts):
    (prefix, *_), items = posts
    for url in (reverse(f"board:{prefix}_create"), reverse(f"board:{prefix}_update", args=[items[0].pk])):
        form = soup(client.get(url, **headers)).find("form", attrs={"enctype": "multipart/form-data"})
        assert form.find("input", attrs={"name": "csrfmiddlewaretoken"})
        assert form.find(attrs={"name": "title"})


@pytest.mark.parametrize("posts", [BOARD_TYPES[0]], ids=["notice"], indirect=True)
def test_notice_create_form_shows_initial_values(client, posts):
    # NoticeForm sets priority/sorting_sequence initial = 0; the create form must show them
    form = soup(client.get(reverse("board:notice_create"), **headers)).find("form", attrs={"enctype": "multipart/form-data"})
    assert form.find("input", attrs={"name": "priority"})["value"] == "0"
    assert form.find("input", attrs={"name": "sorting_sequence"})["value"] == "0"
    assert "None" not in str(form)


# ---------- contract ----------

@param
def test_list_title_and_number_links_match_board(client, posts):
    (prefix, _, heading), items = posts
    page = soup(client.get(reverse(f"board:{prefix}_list"), **headers))
    assert len(page.find_all("title")) == 1 and heading in page.title.get_text()
    assert len(page.find_all("h1")) == 1 and heading in page.h1.get_text()
    assert len(page.find_all("main")) == 1
    detail_links = {a["href"] for a in page.find_all("a", href=True) if "/detail/" in a["href"]}
    assert detail_links == {reverse(f"board:{prefix}_detail", args=[p.pk]) for p in items}


@param
def test_detail_single_title_heading_article(client, posts):
    # board detail has no prev/next navigation (unlike blog); only structure is asserted
    (prefix, *_), items = posts
    page = soup(client.get(reverse(f"board:{prefix}_detail", args=[items[1].pk]), **headers))
    assert len(page.find_all("title")) == 1
    assert len(page.find_all("h1")) == 1 and items[1].title in page.h1.get_text()
    assert len(page.find_all("main")) == 1 and page.find("article")
