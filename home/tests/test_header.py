"""Header: menu icons (admin input never reaches the class attribute unchecked) and the tool row forms."""
from collections import Counter
from types import SimpleNamespace

import pytest
from bs4 import BeautifulSoup
from django.urls import reverse

from home.models.default import MainMenu
from home.templatetags.home_tag import menu_icon_class

headers = {"HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0"}


def node(icon="", path=""):
    return SimpleNamespace(menu_icon=icon, menu_path=path)


@pytest.mark.parametrize("icon, path, expected", [
    ("lni-code", "blog:project_list", "lni-code"),
    (" lni-home ", "", "lni-home"),
    ("", "home:index", "lni-home"),
    ("", "portfolio:portfolio", "lni-briefcase"),
    ("", "blog:blog_list", "lni-pencil-alt"),
    ("", "board:notice_list", "lni-clipboard"),
    ("", "", "lni-link"),
    ("", "users:profile", "lni-link"),
    ('lni-x" onmouseover="alert(1)', "blog:books_list", "lni-pencil-alt"),
    ("lni-home\n", "board:notice_list", "lni-home"),
    ("lni-home extra", "board:notice_list", "lni-clipboard"),
    ("LNI-HOME", "", "lni-link"),
    ("fa fa-home", "home:index", "lni-home"),
    (None, None, "lni-link"),
])
def test_menu_icon_class(icon, path, expected):
    assert menu_icon_class(node(icon, path)) == expected


def page(client):
    response = client.get(reverse("home:search_queryset"), {"keyword": "x"}, **headers)
    assert response.status_code == 200
    return BeautifulSoup(response.content.decode(), "html.parser")


@pytest.mark.django_db
def test_header_menu_shows_icons_and_never_raw_icon_input(client):
    MainMenu.objects.create(menu_name="Home", menu_path="home:index", menu_icon='lni-x" onclick="alert(1)')
    MainMenu.objects.create(menu_name="Out", menu_link="https://example.com/")
    soup = page(client)
    html = str(soup)
    assert "onclick" not in html
    icons = {a.get_text(strip=True): a.find("i")["class"] for a in soup.select("#nav > .nav-item > a")}
    assert icons["Home"] == ["lni", "lni-home"] and icons["Out"] == ["lni", "lni-link"]
    mobile = {a.get_text(strip=True): a.find("i")["class"] for a in soup.select("#menu .offcanvas_main_menu > .nav-item > a")}
    assert mobile["Home"] == ["lni", "lni-home"]


@pytest.mark.django_db
def test_header_tool_row_forms_keep_their_contract_and_ids_are_unique(client):
    soup = page(client)
    ids = Counter(tag["id"] for tag in soup.find_all(id=True))
    assert [i for i, n in ids.items() if n > 1] == []

    search = soup.select_one("#header_navbar form#search_form")
    assert search["method"] == "get" and search["action"] == reverse("home:search_queryset")
    assert search.find("input", id="site-search")["name"] == "keyword"
    assert soup.find("label", attrs={"for": "site-search"})

    lang = soup.select_one("#header_navbar form.header-lang")
    assert lang["method"] == "post" and lang["action"] == reverse("set_language")
    assert lang.find("input", attrs={"name": "csrfmiddlewaretoken"})
    assert lang.find("select", id="site-lang").has_attr("data-autosubmit")
    assert soup.find("label", attrs={"for": "site-lang"})

    # the off-canvas menu carries its own copies for small screens
    assert soup.select_one("#mobile-menu form[role=search] input[name=keyword]")
    m_lang = soup.select_one("#mobile-menu form.header-lang")
    assert m_lang.find("input", attrs={"name": "csrfmiddlewaretoken"}) and m_lang.find("select", attrs={"name": "language"})
    for f in soup.select("#mobile-menu form"):
        for field in f.find_all(["input", "select"], id=True):
            assert soup.find("label", attrs={"for": field["id"]})


@pytest.mark.django_db
def test_theme_toggle_has_both_icons_and_keeps_its_label(client):
    button = page(client).select_one("button[data-theme-toggle]")
    assert button["aria-label"]
    assert button.select_one("svg use")["href"].endswith("#moon-stars")
    assert button.select_one("i.lni-sun")
