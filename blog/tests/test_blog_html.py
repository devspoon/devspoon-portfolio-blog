import pytest
from django.urls import reverse

from blog.models.blog import ProjectPostMixin
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
        **headers,
    )
    assert response.status_code == 302
    queryset = ProjectPostMixin.objects.filter(
        title="test",
        content="<p>hello<br></p>",
    )
    assert queryset.exists()
    assert response.url == reverse(
        "blog:project_list",
    )


@pytest.mark.blog
@pytest.mark.django_db
def test_blog_project_update(staff):
    url = reverse("blog:project_create")
    response = staff.post(
        path=url,
        data={
            "title": "test",
            "content": "hello",
            "dev_lang": "python",
            "repository": "http://github.com/test",
            "version": "1.0.0",
            "role": 0,
            "branch": 0,
        },
        **headers,
    )
    assert response.status_code == 302
    queryset = ProjectPostMixin.objects.filter(
        title="test",
    )
    assert "hello" in queryset.values()[0]["content"]
    url = reverse("blog:project_update", kwargs={"pk": queryset.values()[0]["id"]})
    response = staff.post(
        path=url,
        data={
            "title": "test",
            "content": "bye",
            "dev_lang": "python",
            "repository": "http://github.com/test",
            "version": "1.0.0",
            "role": 0,
            "branch": 0,
        },
        **headers,
    )
    queryset = ProjectPostMixin.objects.filter(
        title="test",
    )
    assert "bye" in queryset.values()[0]["content"]


@pytest.mark.blog
@pytest.mark.django_db
def test_blog_project_delete(staff):
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
        **headers,
    )
    assert response.status_code == 302
    queryset = ProjectPostMixin.objects.filter(
        title="test",
    )
    assert queryset.exists()
    url = reverse("blog:project_delete", kwargs={"pk": queryset.values()[0]["id"]})
    response = staff.get(
        path=url,
        **headers,
    )
    queryset = ProjectPostMixin.objects.filter(
        title="test",
    )
    assert queryset[0].is_deleted is True
