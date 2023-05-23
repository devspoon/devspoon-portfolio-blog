import pytest
from django.urls import reverse

from users.models import User

headers = {
    "HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}


@pytest.mark.blog
@pytest.mark.django_db
def test_blog_project_list_user(user):
    url = reverse("blog:project_list")
    response = user.get(path=url, **headers)
    content = response.content.decode("utf-8")
    assert "project" in content
    assert "write" not in content


@pytest.mark.blog
@pytest.mark.django_db
def test_blog_project_list_staff(staff):
    url = reverse("blog:project_list")
    response = staff.get(path=url, **headers)
    content = response.content.decode("utf-8")
    user = User.objects.get(username="testuser")
    assert user.is_staff is True
    assert "project" in content
    assert "write" in content


# @pytest.mark.blog
# @pytest.mark.django_db
# def test_blog_opensource_detail(client, pk):
#     url = reverse("blog:project_detail", kwargs={"pk": pk})
#     response = client.get(path=url, **headers)
#     content = response.content.decode("utf-8")
#     assert "illust" in content
