"""Tech-stack diagram counts (ADR-016): visible posts per stack tag across the blog types, case/space-insensitive."""

import pytest

from blog.models.blog import BlogPost, ProjectPost
from portfolio.views import STACK, stack_counts
from users.models import User


@pytest.mark.django_db
def test_stack_counts_visible_posts_per_tag_across_types():
    author = User.objects.create_user(username="a", email="a@example.com", nickname="a", password="password")

    def post(model, tags, **kw):
        p = model.objects.create(author=author, title="t", content="c", **kw)
        p.tag_save(tags)

    post(BlogPost, "Django, redis")
    post(BlogPost, "django")
    post(ProjectPost, " django,mysql")
    post(BlogPost, "django", is_hidden=True)     # hidden posts are not counted
    post(BlogPost, "django", is_deleted=True)    # nor deleted ones

    counts = stack_counts()

    assert list(counts) == list(STACK)          # diagram order, every node present
    assert counts["django"] == 3                # "Django", "django", " django" are one node
    assert counts["redis"] == 1 and counts["mysql"] == 1
    assert counts["celery"] == 0


@pytest.mark.django_db
def test_portfolio_renders_timeline_on_the_server(client):
    from datetime import datetime, timezone

    from django.core.cache import cache
    from django.urls import reverse

    from portfolio.models import WorkExperience

    cache.clear()
    for lang in ("0", "1"):  # whichever language the request resolves to
        WorkExperience.objects.create(language=lang, title="Built the search API", summary="FastAPI + Redis",
                                      content="<p>details</p>", project_start_date=datetime(2024, 3, 1, tzinfo=timezone.utc))
    html = client.get(reverse("portfolio:portfolio"), HTTP_USER_AGENT="Mozilla/5.0 Chrome/112.0").content.decode()
    assert "Built the search API" in html and ">2024<" in html   # grouped under its year
    assert "portfolio.js" not in html


@pytest.mark.django_db
def test_experience_title_and_summary_render_admin_html(client):
    """title and summary are summernote fields in the portfolio admin: show their markup, not the tags as text."""
    from datetime import datetime, timezone

    from django.core.cache import cache
    from django.urls import reverse

    from portfolio.models import WorkExperience

    cache.clear()
    for lang in ("0", "1"):
        WorkExperience.objects.create(
            language=lang,
            title='<p><font color="#ff69b4"><b>Freelance</b></font></p>',
            summary="<p>UI test service</p>",
            content="<p>details</p>",
            project_start_date=datetime(2025, 4, 1, tzinfo=timezone.utc),
        )
    html = client.get(reverse("portfolio:portfolio"), HTTP_USER_AGENT="Mozilla/5.0 Chrome/112.0").content.decode()
    assert '<font color="#ff69b4"><b>Freelance</b></font>' in html
    assert "<p>UI test service</p>" in html
    assert "&lt;p&gt;" not in html


@pytest.mark.django_db
def test_interest_title_renders_admin_html(client):
    """InterestedIn.title is a summernote field: '&nbsp;&amp;' must not reach the page as visible text."""
    from django.core.cache import cache
    from django.urls import reverse

    from portfolio.models import InterestedIn

    cache.clear()
    for lang in ("0", "1"):
        InterestedIn.objects.create(language=lang, title="<p>AI&nbsp;&amp;&nbsp;MACHINE LEARNING</p>", content="<p>TTS, STT</p>")
    html = client.get(reverse("portfolio:portfolio"), HTTP_USER_AGENT="Mozilla/5.0 Chrome/112.0").content.decode()
    assert "<p>AI&nbsp;&amp;&nbsp;MACHINE LEARNING</p>" in html
    assert "&amp;nbsp;" not in html
