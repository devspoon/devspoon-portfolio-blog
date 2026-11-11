from unittest import mock

import pytest
from django.test import override_settings
from django.urls import reverse

from portfolio.forms import GetInTouchForm
from portfolio.models import GetInTouchLog

from .test_get_in_touch_form import payload
from .test_get_in_touch_view import HEADERS

pytestmark = pytest.mark.portfolio

RECAPTCHA_KEYS = {
    "RECAPTCHA_PUBLIC_KEY": "test-public-key",
    "RECAPTCHA_PRIVATE_KEY": "test-private-key",
}


def recaptcha_result(is_valid):
    """captcha.client.submit()의 반환값을 흉내낸다. 네트워크를 타지 않는다."""
    return mock.Mock(is_valid=is_valid, error_codes=[], extra_data={})


def test_captcha_is_absent_when_disabled():
    assert "captcha" not in GetInTouchForm().fields


@override_settings(CONTACT_FORM_CAPTCHA=True, **RECAPTCHA_KEYS)
def test_captcha_is_added_when_enabled():
    assert "captcha" in GetInTouchForm().fields


@override_settings(CONTACT_FORM_CAPTCHA=True, **RECAPTCHA_KEYS)
def test_captcha_widget_renders_with_the_site_key():
    html = str(GetInTouchForm()["captcha"])

    assert "g-recaptcha" in html
    assert 'data-sitekey="test-public-key"' in html


@override_settings(CONTACT_FORM_CAPTCHA=True, **RECAPTCHA_KEYS)
def test_missing_captcha_response_is_rejected():
    form = GetInTouchForm(payload())

    assert not form.is_valid()
    assert "captcha" in form.errors


@override_settings(CONTACT_FORM_CAPTCHA=True, **RECAPTCHA_KEYS)
def test_failed_captcha_is_rejected():
    with mock.patch(
        "captcha.fields.client.submit", return_value=recaptcha_result(False)
    ):
        form = GetInTouchForm(payload(**{"g-recaptcha-response": "token"}))

        assert not form.is_valid()
        assert "captcha" in form.errors


@override_settings(CONTACT_FORM_CAPTCHA=True, **RECAPTCHA_KEYS)
def test_passing_captcha_is_accepted():
    with mock.patch(
        "captcha.fields.client.submit", return_value=recaptcha_result(True)
    ):
        form = GetInTouchForm(payload(**{"g-recaptcha-response": "token"}))

        assert form.is_valid(), form.errors


@pytest.mark.django_db
@override_settings(CONTACT_FORM_CAPTCHA=True, **RECAPTCHA_KEYS)
def test_view_rejects_submission_without_captcha(client):
    response = client.post(reverse("portfolio:mail"), payload(), **HEADERS)

    assert response.status_code == 302
    assert GetInTouchLog.objects.count() == 0


@pytest.mark.django_db
def test_portfolio_page_provides_the_form(client):
    """폼은 캐시가 아니라 요청마다 새로 만들어져야 한다."""
    first = client.get(reverse("portfolio:portfolio"), **HEADERS)
    second = client.get(reverse("portfolio:portfolio"), **HEADERS)

    form = first.context["get_in_touch_form"]
    assert isinstance(form, GetInTouchForm)
    assert second.context["get_in_touch_form"] is not form
