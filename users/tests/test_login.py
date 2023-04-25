import pytest
from django.urls import reverse

from users.models import UserProfile

pytestmark = pytest.mark.django_db

headers = {
    "HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "email, password",
    [
        ("test@test.com", "test1324"),
    ],
)
def test_login_success(client, static_user, email, password):
    login_url = reverse("users:login")
    data = {"email": email, "password": password}

    response = client.post(
        path=login_url,
        data=data,
        **headers,
    )

    assert response.status_code == 302
    assert response.url == reverse("home:index")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "email, password",
    [
        ("test@test.com", "test132444"),
    ],
)
def test_login_fail(client, static_user, email, password):
    login_url = reverse("users:login")
    data = {"email": email, "password": password}
    response = client.post(
        path=login_url,
        data=data,
        **headers,
    )
    assert response.status_code == 302
    assert response.url == reverse("users:login")


@pytest.mark.django_db
def test_profile_exist(client, static_user):
    result = UserProfile.objects.filter(user=static_user).values()
    assert result.exists() is True
    assert result[0]["nickname"] == "test"
