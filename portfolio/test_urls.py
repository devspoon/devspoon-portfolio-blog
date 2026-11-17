"""The old timeline JSON endpoint is gone (the timeline is server-rendered since phase 3)."""
import pytest
from django.urls import NoReverseMatch, reverse


def test_work_experience_json_route_is_removed():
    with pytest.raises(NoReverseMatch):
        reverse("portfolio:work_experience")


@pytest.mark.django_db
def test_work_experience_json_url_returns_404(client):
    assert client.get("/portfolio/json/", HTTP_USER_AGENT="Mozilla/5.0 Chrome/112.0").status_code == 404
