"""The project card shows its title once, in the top band, with or without a thumbnail; the body has no heading."""
import pytest
from bs4 import BeautifulSoup
from django.template.loader import render_to_string


@pytest.mark.parametrize("image", ["/media/p.png", ""])
def test_project_card_title_is_in_the_top_band_once(image):
    post = {"pk": 1, "title": "Sample project", "title_image": image, "content": "<p>body</p>",
            "author": {"username": "login-id", "nickname": ""}}
    soup = BeautifulSoup(render_to_string("home/_project_card.html", {"post": post}), "html.parser")

    assert soup.get_text().count("Sample project") == 1
    titles = soup.select(".card-img h3.card-title")
    assert len(titles) == 1
    assert [a["href"] for a in titles[0].select("a")] == ["/blog/project/detail/1/"]
    assert not soup.select_one(".card-content").find(["h1", "h2", "h3", "h4", "h5", "h6"])
    assert bool(soup.select_one(".card-img img")) == bool(image)
    assert bool(soup.select_one(".card-img .card-img-empty")) == (not image)
    # one link to the post per card (the thumbnail is no longer a second link)
    assert len(soup.find_all("a", href="/blog/project/detail/1/")) == 1


def test_project_card_keeps_the_theme_body_and_a_readable_long_title():
    long_title = "아주 긴 한글 제목 " * 8
    post = {"pk": 1, "title": long_title, "title_image": "", "content": "<p>body</p>", "dev_lang": "python, rust",
            "version": "1.2.3", "repository": "https://github.com/ex/" + "x" * 80,
            "author": {"username": "login-id", "nickname": "Nick"}}
    soup = BeautifulSoup(render_to_string("home/_project_card.html", {"post": post}), "html.parser")

    assert soup.select_one(".card-title a")["title"] == long_title     # the clamped title stays readable on hover
    assert soup.select_one(".card-img .product-action a.share")["href"] == post["repository"]
    assert soup.select_one(".card-content > span.update").get_text() == "body"
    cells = [c.get_text(" ", strip=True) for c in soup.select(".card-content > .project-info.row > .col-6")]
    assert "python, rust" in cells and "1.2.3" in cells
    assert cells[-1] == "Nick"


def test_project_card_author_shows_nickname_never_login_name():
    post = {"pk": 1, "title": "t", "title_image": "", "content": "", "author": {"username": "login-id", "nickname": ""}}
    html = render_to_string("home/_project_card.html", {"post": post})
    assert "login-id" not in html
    post["author"]["nickname"] = "Writer Nick"
    assert "Writer Nick" in render_to_string("home/_project_card.html", {"post": post})


@pytest.mark.parametrize("image", ["/media/p.png", ""])
def test_latest_post_card_title_is_in_the_top_band_once(image):
    from django.urls import reverse

    item = {"pk": 3, "table": "Blog", "title": "Latest post", "title_image": image, "content": "<p>body</p>",
            "reply_count": 0, "visit_count": 0}
    soup = BeautifulSoup(render_to_string("home/_post_link.html", {"item": item}), "html.parser")

    titles = soup.select(".card-img h3.card-title")
    assert len(titles) == 1 and titles[0].get_text(strip=True) == "Latest post"
    assert not soup.select_one(".card-content").find(["h1", "h2", "h3", "h4", "h5", "h6"])
    assert len(soup.find_all("a", href=reverse("blog:blog_detail", args=[3]))) == 1
    assert soup.select_one(".card-content .blog-info.row > .col-6 a.category")
