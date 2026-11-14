"""Tags survive an edit: the update form shows them comma-separated, and saving trims and de-duplicates."""
import pytest

from blog.models.blog import BlogPost, BooksPost, OnlineStudyPost, OpenSourcePost, ProjectPost
from blog.views.blog.blog_forms import BlogForm
from blog.views.books.books_forms import BooksForm
from blog.views.online_study.online_study_forms import OnlineStudyForm
from blog.views.opensource.opensource_forms import OpenSourceForm
from blog.views.project.project_forms import ProjectForm
from users.models import User

pytestmark = [pytest.mark.blog, pytest.mark.django_db]

FORMS = [(BlogForm, BlogPost, {}), (BooksForm, BooksPost, {}), (OnlineStudyForm, OnlineStudyPost, {}),
         (OpenSourceForm, OpenSourcePost, {}), (ProjectForm, ProjectPost, {})]


@pytest.fixture
def author():
    return User.objects.create_user(username="author", password="password", is_staff=True)


def tags_of(post):
    return sorted(t.tag for t in post.tag_set.all())


@pytest.mark.parametrize("form_class, model, extra", FORMS, ids=[f[0].__name__ for f in FORMS])
def test_update_form_round_trips_tags(author, form_class, model, extra):
    post = model.objects.create(author=author, title="t", content="<p>c</p>", **extra)
    post.tag_save("django,python")
    initial = form_class(instance=post).fields["tag_set"].initial
    post.tag_save(initial)  # saving the form unchanged must keep the same tags
    assert tags_of(post) == ["django", "python"]


def test_tag_save_trims_dedups_and_skips_empty(author):
    post = BlogPost.objects.create(author=author, title="t", content="<p>c</p>")
    post.tag_save(" django, python ,,django, ")
    assert tags_of(post) == ["django", "python"]


def test_tag_save_with_empty_input_clears_tags(author):
    post = BlogPost.objects.create(author=author, title="t", content="<p>c</p>")
    post.tag_save("django")
    post.tag_save("")
    assert tags_of(post) == []
