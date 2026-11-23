"""Header account name, POST-only logout, login ?next and the autocomplete hints on the auth forms."""
import pytest
from bs4 import BeautifulSoup
from django.template.loader import render_to_string
from django.urls import reverse

from users.models import User
from users.views.users_forms import LoginForm, ProfileForm, RegisterForm, ReplacePasswordForm, UpdatePasswordForm

pytestmark = pytest.mark.django_db
headers = {"HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0"}


def header_of(client):
    response = client.get(reverse("home:search_queryset"), {"keyword": "x"}, **headers)
    assert response.status_code == 200
    return BeautifulSoup(response.content.decode(), "html.parser").select_one("#header_navbar")


def logged_in(client, nickname):
    user = User.objects.create_user(username="login-id", email="me@example.com", password="pass12345", nickname=nickname)
    client.force_login(user)
    session = client.session  # LoginView keeps these in the session; the header must not show them
    session["email"], session["username"] = user.email, user.username
    session.save()
    return user


@pytest.mark.parametrize("nickname, shown", [("Writer Nick", "Writer Nick"), ("", "Account")])
def test_header_account_shows_the_nickname_never_the_email_or_login_id(client, nickname, shown):
    logged_in(client, nickname)
    header = header_of(client)
    assert header.select_one(".account-btn__name").get_text(strip=True) == shown
    assert "me@example.com" not in str(header) and "login-id" not in str(header)


def test_logout_is_a_post_form_and_get_does_not_log_out(client):
    logged_in(client, "Nick")
    form = header_of(client).select_one(".dropdown-nav form")
    assert form["method"] == "post" and form["action"] == reverse("users:logout")
    assert form.find("input", attrs={"name": "csrfmiddlewaretoken"}) and form.find("button", type="submit")

    assert client.get(reverse("users:logout"), **headers).status_code == 405
    assert "_auth_user_id" in client.session

    response = client.post(reverse("users:logout"), **headers)
    assert response.status_code == 302 and response.url == reverse("home:index")
    assert "_auth_user_id" not in client.session


def login(client, next_url):
    return client.post(reverse("users:login"), {"email": "test@test.com", "password": "test1324", "next": next_url}, **headers)


def test_login_goes_to_a_same_site_next(client, static_user):
    assert login(client, "/blog/?page=2").url == "/blog/?page=2"


@pytest.mark.parametrize("next_url", ["//evil.com", "https://evil.com/", "http://evil.com/blog/", "javascript:alert(1)"])
def test_login_ignores_an_off_site_next(client, static_user, next_url):
    assert login(client, next_url).url == reverse("home:index")


@pytest.fixture
def social_apps():
    """The login page links the three social providers; allauth needs their SocialApp rows to build the links."""
    from allauth.socialaccount.models import SocialApp
    from django.contrib.sites.models import Site

    for provider in ("google", "kakao", "naver"):
        SocialApp.objects.create(provider=provider, name=provider, client_id="id", secret="s").sites.add(Site.objects.get_current())


def test_login_page_carries_only_a_safe_next(client, social_apps):
    def hidden(next_url):
        soup = BeautifulSoup(client.get(reverse("users:login"), {"next": next_url}, **headers).content.decode(), "html.parser")
        tag = soup.select_one("form input[type=hidden][name=next]")
        return tag and tag["value"]

    assert hidden("/board/notice/") == "/board/notice/"
    assert not hidden("//evil.com")


def test_a_failed_login_keeps_the_next(client, static_user):
    response = client.post(reverse("users:login"), {"email": "test@test.com", "password": "wrong-pass", "next": "/blog/"}, **headers)
    assert response.url == reverse("users:login") + "?next=%2Fblog%2F"


def test_login_page_autocomplete(client, social_apps):
    soup = BeautifulSoup(client.get(reverse("users:login"), **headers).content.decode(), "html.parser")
    assert soup.find("input", attrs={"name": "email"})["autocomplete"] == "username"
    assert soup.find("input", attrs={"name": "password"})["autocomplete"] == "current-password"


@pytest.mark.parametrize("form_class, expected", [
    (LoginForm, {"email": "username", "password": "current-password"}),
    (RegisterForm, {"password": "new-password", "password_confirm": "new-password"}),
    (UpdatePasswordForm, {"new_password": "new-password", "new_password_confirm": "new-password"}),
    (ReplacePasswordForm, {"old_password": "current-password", "new_password": "new-password", "new_password_confirm": "new-password"}),
    (ProfileForm, {"password": "current-password", "new_password": "new-password", "new_password_confirm": "new-password"}),
])
def test_auth_form_fields_render_their_autocomplete(form_class, expected):
    form = form_class()
    for name, value in expected.items():
        soup = BeautifulSoup(render_to_string("components/form_field.html", {"field": form[name]}), "html.parser")
        assert soup.find("input", attrs={"name": name})["autocomplete"] == value
