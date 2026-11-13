import pytest
from bs4 import BeautifulSoup
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize("name", ["home:privacy_policy", "home:terms_of_service"])
def test_policy_pages_have_one_h1(client, name):
    page = BeautifulSoup(client.get(reverse(name)).content, "html.parser")
    assert len(page.select("main h1")) == 1
