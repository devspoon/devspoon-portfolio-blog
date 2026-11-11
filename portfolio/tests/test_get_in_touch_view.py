from unittest import mock

import pytest
from django.contrib.messages import constants as message_levels
from django.core import mail
from django.urls import reverse

from portfolio.models import GetInTouchLog

from .test_get_in_touch_form import TOO_LONG_NUMBER, payload

pytestmark = [pytest.mark.portfolio, pytest.mark.django_db]

HEADERS = {
    "HTTP_USER_AGENT": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    )
}


def post(client, **overrides):
    return client.post(reverse("portfolio:mail"), payload(**overrides), **HEADERS)


def message_levels_of(response):
    return [message.level for message in response.wsgi_request._messages]


def test_valid_inquiry_is_saved_and_mailed(client):
    response = post(client)

    assert response.status_code == 302
    log = GetInTouchLog.objects.get()
    assert log.state is True
    assert log.status == GetInTouchLog.MailStatus.SENT
    assert log.phone_number == "010-1234-5678"
    assert len(mail.outbox) == 1
    assert "project inquiry" in mail.outbox[0].subject


def test_too_long_number_never_reaches_the_database(client):
    """DataError 재발 방지: 저장 시도 자체가 일어나지 않아야 한다."""
    response = post(client, number=TOO_LONG_NUMBER)

    assert response.status_code == 302
    assert GetInTouchLog.objects.count() == 0
    assert len(mail.outbox) == 0
    assert message_levels.ERROR in message_levels_of(response)


@pytest.mark.parametrize("field", ["name", "emailfrom", "subject", "message"])
def test_missing_required_field_is_rejected(client, field):
    response = post(client, **{field: ""})

    assert response.status_code == 302
    assert GetInTouchLog.objects.count() == 0
    assert len(mail.outbox) == 0


def test_mail_failure_still_records_the_inquiry(client):
    with mock.patch("portfolio.views.send_mail_sync", return_value=False):
        response = post(client)

    log = GetInTouchLog.objects.get()
    assert log.state is True
    # 접수는 성공, 발송은 실패로 구분해 남는다.
    assert log.status == GetInTouchLog.MailStatus.FAILED
    # 사용자에게는 성공이 아니라 지연으로 안내한다.
    assert message_levels.SUCCESS not in message_levels_of(response)
    assert message_levels.WARNING in message_levels_of(response)


def test_mail_recipient_is_taken_from_settings_not_the_form(client, settings):
    post(client, emailto="attacker@example.com")

    assert mail.outbox[0].to == [settings.DEFAULT_FROM_EMAIL]


def test_optional_number_can_be_empty(client):
    post(client, number="")

    assert GetInTouchLog.objects.get().phone_number == ""


def test_only_one_log_row_is_created_per_submission(client):
    """이전 구현은 첫 return 뒤에 도달 불가능한 저장 코드가 여러 번 반복됐다."""
    post(client)

    assert GetInTouchLog.objects.count() == 1
