import pytest
from bs4 import BeautifulSoup
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize("name", ["home:privacy_policy", "home:terms_of_service"])
def test_policy_pages_have_one_h1(client, name):
    page = BeautifulSoup(client.get(reverse(name)).content, "html.parser")
    assert len(page.select("main h1")) == 1


@pytest.mark.django_db
def test_font_css_does_not_block_render_and_has_noscript_fallback(client):
    page = BeautifulSoup(client.get(reverse("home:privacy_policy")).content, "html.parser")  # any base.html page
    links = [l for l in page.head.find_all("link", rel="stylesheet") if "pretendard" in l["href"]]
    font = [l for l in links if not l.find_parent("noscript")]
    fallback = [l for l in links if l.find_parent("noscript")]
    assert len(font) == 1 and font[0]["media"] == "print" and "this.media='all'" in font[0]["onload"]
    assert len(fallback) == 1 and fallback[0]["href"] == font[0]["href"] and not fallback[0].get("media")
