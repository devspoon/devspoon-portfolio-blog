import pytest
from django.urls import reverse

from users.models import User

headers = {"HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0"}


@pytest.mark.users
@pytest.mark.django_db
def test_user_delete_get_is_405(user):
    assert user.get(reverse("users:user_delete"), **headers).status_code == 405
    assert User.objects.get(username="testuser").is_deleted is False


@pytest.mark.users
@pytest.mark.django_db
def test_user_delete_anonymous_redirects_to_login(client):
    response = client.post(reverse("users:user_delete"), **headers)
    assert response.status_code == 302
    assert reverse("users:login") in response.url


@pytest.mark.users
@pytest.mark.django_db
def test_user_delete_post_marks_deleted(user):
    pk = User.objects.get(username="testuser").pk
    response = user.post(reverse("users:user_delete"), **headers)
    assert response.status_code == 302
    assert User.objects.get(pk=pk).is_deleted is True
