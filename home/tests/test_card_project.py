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


def test_project_card_author_shows_nickname_never_login_name():
    post = {"pk": 1, "title": "t", "title_image": "", "content": "", "author": {"username": "login-id", "nickname": ""}}
    html = render_to_string("home/_project_card.html", {"post": post})
    assert "login-id" not in html
    post["author"]["nickname"] = "Writer Nick"
    assert "Writer Nick" in render_to_string("home/_project_card.html", {"post": post})
