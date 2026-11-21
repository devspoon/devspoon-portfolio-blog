"""The project card shows its title once, with or without a thumbnail, and the title stays the card link."""
import pytest
from bs4 import BeautifulSoup
from django.template.loader import render_to_string


@pytest.mark.parametrize("image", ["/media/p.png", ""])
def test_project_card_title_appears_once(image):
    post = {"title": "Sample project", "title_image": image, "content": "<p>body</p>"}
    soup = BeautifulSoup(
        render_to_string("components/card_project.html", {"post": post, "url": "/blog/project/detail/1/"}),
        "html.parser",
    )

    assert soup.get_text().count("Sample project") == 1
    titles = soup.select(".c-card__title")
    assert len(titles) == 1
    assert [a["href"] for a in titles[0].select("a")] == ["/blog/project/detail/1/"]
