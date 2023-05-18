import pytest
from django.urls import reverse

headers = {
    "HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}


@pytest.mark.error
@pytest.mark.django_db
def test_error_404(client):
    url = reverse("home:index") + "test.html"
    response = client.get(path=url, **headers)
    content = response.content.decode("utf-8")
    assert "404 Error" in content
