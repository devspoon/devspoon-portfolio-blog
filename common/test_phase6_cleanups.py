"""phase6 소규모 정리 회귀 테스트 (docs/crp/groups/phase6-small-cleanups)."""

import pathlib

import pytest
from bs4 import BeautifulSoup
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import Client, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from blog.models.blog import BlogPost, BooksPost, OnlineStudyPost, OpenSourcePost, ProjectPost, Tag
from blog.models.blog_reply import BlogPostReply
from board.models import Notice
from board.models.board_reply import NoticeReply
from custom_middlewares.middlewares.statistics import ConnectionMethodStatsMiddleware
from portfolio.forms import GetInTouchForm
from users.models import User, UserProfile, UserVerification

headers = {"HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0"}
POSTS = [("blog", BlogPost), ("project", ProjectPost), ("online_study", OnlineStudyPost), ("opensource", OpenSourcePost), ("books", BooksPost)]
post_cases = pytest.mark.parametrize("prefix,model", POSTS, ids=[p[0] for p in POSTS])


def make_user(name, **extra):
    return User.objects.create_user(username=name, email=f"{name}@example.com", nickname=name, password="password", **extra)


def client_for(user):
    c = Client(**headers)
    c.force_login(user)
    return c


def required_values(model):
    """수정 폼이 필수로 요구하는 문자열 필드를 채운다(폼이 그대로 저장되도록)."""
    from django.db import models as m

    values = {}
    for f in model._meta.concrete_fields:
        if isinstance(f, m.CharField) and not f.blank and not f.has_default() and f.name not in ("title", "table_name"):
            values[f.name] = "https://example.com" if isinstance(f, m.URLField) else "x"
        if f.name == "repository":  # 모델은 blank=True지만 폼이 필수로 바꾼다
            values[f.name] = "https://example.com"
    return values


def tag_names(post):
    return sorted(post.tag_set.values_list("tag", flat=True))


# --- F-001·F-002 태그 ----------------------------------------------------------------------------


@pytest.mark.django_db
@post_cases
def test_saving_the_update_form_unchanged_keeps_the_tags(prefix, model):
    author = make_user("author", is_staff=True)
    post = model.objects.create(author=author, title="t", content="<p>c</p>", **required_values(model))
    post.tag_save("python,django")
    c = client_for(author)
    url = reverse(f"blog:{prefix}_update", args=[post.pk])
    form = BeautifulSoup(c.get(url).content, "html.parser").find("input", attrs={"name": "tag_set"}).find_parent("form")
    data = {}
    for field in form.find_all(["input", "textarea", "select"]):
        name = field.get("name")
        if not name or field.get("type") in ("file", "submit"):
            continue
        if field.name == "textarea":
            data[name] = field.text
        elif field.name == "select":
            chosen = field.find("option", selected=True) or field.find("option")
            data[name] = chosen.get("value", "") if chosen else ""
        elif field.get("type") == "checkbox":
            if field.has_attr("checked"):
                data[name] = field.get("value", "on")
        else:
            data[name] = field.get("value", "")
    assert sorted(data["tag_set"].split(",")) == ["django", "python"]
    response = c.post(url, data)
    assert response.status_code == 302, response.context["form"].errors
    assert tag_names(post) == ["django", "python"]


@pytest.mark.django_db
def test_tag_save_strips_spaces_and_drops_blanks_and_duplicates():
    post = BlogPost.objects.create(author=make_user("a"), title="t", content="<p>c</p>")
    post.tag_save(" python , django,,python, ")
    assert tag_names(post) == ["django", "python"]
    assert not Tag.objects.filter(tag__startswith=" ").exists()
    post.tag_save("")
    assert tag_names(post) == []


@pytest.mark.django_db
def test_too_long_tag_is_a_form_error():
    author = make_user("author", is_staff=True)
    c = client_for(author)
    data = {"title": "t", "content": "<p>c</p>", "tag_set": "ok," + "x" * 141}
    response = c.post(reverse("blog:blog_create"), data)
    assert response.status_code == 200 and "tag_set" in response.context["form"].errors
    assert not BlogPost.objects.exists()
    data["tag_set"] = "ok," + "x" * 140
    assert c.post(reverse("blog:blog_create"), data).status_code == 302


# --- F-003 태그 검색 -----------------------------------------------------------------------------


@pytest.mark.django_db
def test_tag_search_pages_the_results_and_shows_the_tag_text():
    author = make_user("a")
    for i in range(12):
        BlogPost.objects.create(author=author, title=f"post{i}", content="<p>c</p>").tag_save("python")
    c = Client(**headers)
    first = c.get(reverse("home:search_queryset"), {"tag": "python"})
    assert len(first.context["board"]) == 10
    assert first.context["tag"] == "python"
    page = BeautifulSoup(first.content, "html.parser")
    assert "python" in page.find("h1").text and "QuerySet" not in page.find("h1").text
    assert len(c.get(reverse("home:search_queryset"), {"tag": "python", "page": 2}).context["board"]) == 2


# --- F-004 닉네임 -------------------------------------------------------------------------------


@pytest.mark.django_db
def test_profile_nickname_never_collides():
    make_user("kim")  # 프로필 닉네임 kim
    social = User.objects.create_user(username="social1", email="kim@other.com", password="password")  # 닉네임 없음 → 이메일 앞부분 kim
    chosen = User.objects.create_user(username="lee", email="lee@example.com", nickname="kim1", password="password")  # 이미 쓰인 kim1
    nicknames = list(UserProfile.objects.values_list("nickname", flat=True))
    assert len(nicknames) == len(set(nicknames)) == 3
    assert UserProfile.objects.get(user=social).nickname == "kim1" and UserProfile.objects.get(user=chosen).nickname == "kim11"


# --- F-005 첨부 파일 정리 ------------------------------------------------------------------------


@pytest.mark.django_db
def test_replacing_file2_removes_the_old_file_even_when_file1_is_empty(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)
    post = BlogPost.objects.create(author=make_user("a"), title="t", content="<p>c</p>", file2=SimpleUploadedFile("old.txt", b"old"))
    old_path = post.file2.path
    post.file2 = SimpleUploadedFile("new.txt", b"new")
    post.save()
    assert post.file2.path != old_path and not pathlib.Path(old_path).exists()


# --- F-006·F-010 이메일 도메인 ------------------------------------------------------------------


@override_settings(EMAIL_DNS_VALIDATION=False)
@pytest.mark.parametrize("email,ok", [("a@contest.com", True), ("a@latest.io", True), ("a@test.com", False), ("a@mail.test.co.kr", False), ("a@x.test", False)])
def test_contact_form_rejects_only_test_domains(email, ok):
    form = GetInTouchForm({"name": "kim", "emailfrom": email, "number": "", "subject": "s", "message": "m"})
    form.is_valid()
    assert ("emailfrom" not in form.errors) is ok


@pytest.mark.parametrize("email,ok", [("a@contest.com", True), ("a@test.com", False)])
def test_register_form_rejects_test_domains_without_crashing(monkeypatch, email, ok):
    from users.views import users_forms

    monkeypatch.setattr(users_forms, "validate_email", lambda **kwargs: True)  # DNS 조회 없이
    assert bool(users_forms.RegisterForm().check_email_validation_with_dns(email)) is ok


def test_register_form_dns_failure_is_a_rejection_not_a_crash(monkeypatch):
    from users.views import users_forms

    def fail(**kwargs):
        raise users_forms.Error("dns down")

    monkeypatch.setattr(users_forms, "validate_email", fail)
    assert not users_forms.RegisterForm().check_email_validation_with_dns("a@example.com")


# --- F-007 mac 통계 -----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "ua,field",
    [
        ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15", "mac"),
        ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148", "iph"),
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0", "win"),
        ("Mozilla/5.0 (Linux; Android 14) Chrome/112.0 Mobile", "android"),
    ],
)
def test_os_stats_resolve_mac(ua, field):
    assert ConnectionMethodStatsMiddleware.resolve_field(ua) == field


# --- F-008 admin 목록 쿼리 수 --------------------------------------------------------------------


def _blog_post(i, author):
    return BlogPost.objects.create(author=author, title=f"t{i}", content="<p>c</p>")


ADMIN_CASES = [
    ("blog_admin:blog_blogpost_changelist", lambda i, a: _blog_post(i, a).tag_save(f"tag{i}")),
    ("blog_admin:blog_blogpostreply_changelist", lambda i, a: BlogPostReply.objects.create(author=a, post=_blog_post(i, a), comment="c")),
    ("board_admin:board_notice_changelist", lambda i, a: Notice.objects.create(author=a, title=f"t{i}", content="<p>c</p>")),
    ("board_admin:board_noticereply_changelist", lambda i, a: NoticeReply.objects.create(author=a, board=Notice.objects.create(author=a, title=f"t{i}", content="c"), comment="c")),
    ("user_admin:users_userprofile_changelist", lambda i, a: make_user(f"u{i}")),
    ("user_admin:users_userverification_changelist", lambda i, a: UserVerification.objects.create(user=make_user(f"v{i}"), verify_name=0, key=f"k{i}")),
]


@pytest.mark.django_db
@pytest.mark.parametrize("url_name,make", ADMIN_CASES, ids=[c[0] for c in ADMIN_CASES])
def test_admin_changelist_queries_do_not_grow_with_rows(url_name, make):
    admin = User.objects.create_superuser(username="root", email="root@example.com", nickname="root", password="password")
    c = client_for(admin)
    url = reverse(url_name)

    def count():
        c.get(url)  # 세션·권한 캐시를 데운다
        with CaptureQueriesContext(connection) as ctx:
            assert c.get(url).status_code == 200
        return len(ctx)

    make(0, admin)
    one = count()
    for i in range(1, 10):
        make(i, admin)
    # 세션·권한 확인 쿼리가 ±1~2 흔들린다. N+1이면 행 9개에 9개 이상 늘어난다.
    assert count() - one < 9
