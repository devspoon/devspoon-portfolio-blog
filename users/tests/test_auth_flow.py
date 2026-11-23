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
