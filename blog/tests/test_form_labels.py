"""Post forms show human labels, not field names; the update form still finds attachments by field name."""
import pytest
from bs4 import BeautifulSoup
from django.urls import reverse

from blog.models.blog import BlogPost
from blog.views.blog.blog_forms import BlogForm
from blog.views.books.books_forms import BooksForm
from blog.views.online_study.online_study_forms import OnlineStudyForm
from blog.views.opensource.opensource_forms import OpenSourceForm
from blog.views.project.project_forms import ProjectForm
from board.views.notice.notice_forms import NoticeForm
from board.views.reactivation.reactivation_forms import ReactivationForm
from board.views.visiter.visiter_forms import VisiterForm
from users.models import User

FORMS = [BlogForm, BooksForm, OnlineStudyForm, OpenSourceForm, ProjectForm, NoticeForm, ReactivationForm, VisiterForm]


@pytest.mark.parametrize("form_class", FORMS, ids=[f.__name__ for f in FORMS])
def test_labels_are_words_not_field_names(form_class):
    for name, field in form_class().fields.items():
        label = str(field.label)
        assert label and label != name and label[0].isupper() and "_" not in label, (name, label)


@pytest.mark.django_db
def test_update_form_shows_current_attachment(client):
    staff = User.objects.create_user(username="author", password="password", is_staff=True)
    client.login(username="author", password="password")
    post = BlogPost.objects.create(author=staff, title="t", content="<p>c</p>", file1="blog/files/report.pdf")
    page = BeautifulSoup(client.get(reverse("blog:blog_update", args=[post.pk]),
                                    HTTP_USER_AGENT="Mozilla/5.0 Chrome/112.0").content, "html.parser")
    assert "report.pdf" in page.get_text()
