"""CORS only trusts the site's own origins, and Google Analytics loads only where settings enable it."""
import pytest
from django.conf import settings
from django.test import override_settings

pytestmark = pytest.mark.django_db
PAGE = "/terms-of-service"
UA = {"HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0"}


def test_cors_allows_listed_origins_only():
    assert settings.CORS_ALLOW_ALL_ORIGINS is False
    assert settings.CORS_ALLOWED_ORIGINS and all("://" in o for o in settings.CORS_ALLOWED_ORIGINS)


def test_foreign_origin_gets_no_cors_grant(client):
    response = client.get(PAGE, HTTP_ORIGIN="https://evil.example", **UA)
    assert "Access-Control-Allow-Origin" not in response.headers


def test_analytics_is_off_by_default(client):
    assert b"googletagmanager" not in client.get(PAGE, **UA).content


@override_settings(ANALYTICS_ENABLED=True)
def test_analytics_loads_when_enabled(client):
    assert b"googletagmanager" in client.get(PAGE, **UA).content
