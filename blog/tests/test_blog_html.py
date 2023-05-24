import pytest
from django.urls import reverse

from blog.models.blog import ProjectPost
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
    # The write button is not visible to normal users
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
    # The write button is visible to staff users.
    assert "write" in content


@pytest.mark.blog
@pytest.mark.django_db
def test_blog_project_create(staff):
    url = reverse("blog:project_create")
    response = staff.post(
        path=url,
        data={
            "title": "test",
            "content": "<p>hello<br></p>",
            "dev_lang": "python",
            "repository": "http://github.com/test",
            "version": "1.0.0",
            "role": 0,
            "branch": 0,
        },
        **headers
    )
    assert response.status_code == 302
    queryset = ProjectPost.objects.filter(
        title="test",
        content="<p>hello<br></p>",
    )
    assert queryset.exists()
    assert response.url == reverse(
        "blog:project_list",
    )


# @pytest.mark.blog
# @pytest.mark.django_db
# def test_blog_project_update(client, pk):
#     url = reverse("blog:project_update", kwargs={"pk": pk})
#     response = client.get(path=url, **headers)
#     content = response.content.decode("utf-8")
#     assert "illust" in content


# @pytest.mark.blog
# @pytest.mark.django_db
# def test_blog_project_delete(client, pk):
#     url = reverse("blog:project_delete", kwargs={"pk": pk})
#     response = client.get(path=url, **headers)
#     content = response.content.decode("utf-8")
#     assert "illust" in content
