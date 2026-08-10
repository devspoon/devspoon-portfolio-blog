import pytest
from django.core.exceptions import DisallowedHost, SuspiciousOperation
from django.http import Http404

from config.settings.sub_settings.system.sentry import before_send

pytestmark = pytest.mark.middlewares


def event(url="https://devspoon.com/portfolio/"):
    return {"request": {"url": url}}


def hint(exception=None):
    if exception is None:
        return {}
    return {"exc_info": (type(exception), exception, None)}


@pytest.mark.parametrize(
    "exception",
    [
        Http404("no such page"),
        DisallowedHost("Invalid HTTP_HOST header"),
        SuspiciousOperation("bad request"),
    ],
)
def test_scanner_exceptions_are_dropped(exception):
    assert before_send(event(), hint(exception)) is None


@pytest.mark.parametrize(
    "url",
    [
        "https://devspoon.com/wp.php",
        "https://devspoon.com/bbs/board.php?bo_table=free",
        "https://devspoon.com/site/phpinfo.php",
        "https://devspoon.com/wp-admin/",
        "https://devspoon.com/.env",
    ],
)
def test_scanner_paths_are_dropped(url):
    assert before_send(event(url), hint(ValueError("boom"))) is None


def test_real_errors_are_kept():
    payload = event()

    assert before_send(payload, hint(ValueError("boom"))) is payload


def test_event_without_request_is_kept():
    payload = {}

    assert before_send(payload, hint(ValueError("boom"))) is payload
