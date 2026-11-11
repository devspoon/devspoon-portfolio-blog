from unittest import mock

import pytest
from django.core import mail

from utils.email.async_send_email import (
    mask_email,
    mask_recipients,
    send_mail_sync,
)

pytestmark = pytest.mark.portfolio


@pytest.mark.parametrize(
    "address,expected",
    [
        ("hong.gildong@gmail.com", "h***g@gmail.com"),
        ("ab@gmail.com", "a*@gmail.com"),
        ("a@gmail.com", "a*@gmail.com"),
        ("not-an-email", "***"),
        ("", "***"),
        (None, "***"),
    ],
)
def test_mask_email(address, expected):
    assert mask_email(address) == expected


def test_mask_recipients():
    assert mask_recipients(["hong.gildong@gmail.com"]) == ["h***g@gmail.com"]
    assert mask_recipients([]) == []
    assert mask_recipients(None) == []


def test_send_mail_sync_reports_success():
    delivered = send_mail_sync(
        subject="hello",
        recipient_list=["admin@devspoon.com"],
        message="body",
        from_email="admin@devspoon.com",
    )

    assert delivered is True
    assert len(mail.outbox) == 1


def test_send_mail_sync_reports_vendor_failure():
    """SendGrid 401 / Maximum credits exceeded 같은 외부 실패를 흡수한다."""
    with mock.patch(
        "django.core.mail.EmailMultiAlternatives.send",
        side_effect=Exception("HTTP Error 401: Unauthorized"),
    ):
        delivered = send_mail_sync(
            subject="hello",
            recipient_list=["admin@devspoon.com"],
            message="body",
            from_email="admin@devspoon.com",
        )

    assert delivered is False


def test_send_mail_sync_reports_zero_recipients():
    with mock.patch(
        "django.core.mail.EmailMultiAlternatives.send", return_value=0
    ):
        delivered = send_mail_sync(
            subject="hello",
            recipient_list=["admin@devspoon.com"],
            message="body",
            from_email="admin@devspoon.com",
        )

    assert delivered is False


def test_failure_log_does_not_leak_the_recipient(caplog):
    with mock.patch(
        "django.core.mail.EmailMultiAlternatives.send",
        side_effect=Exception("HTTP Error 401: Unauthorized"),
    ):
        send_mail_sync(
            subject="hello",
            recipient_list=["hong.gildong@gmail.com"],
            message="body",
            from_email="admin@devspoon.com",
        )

    logged = [record.recipients for record in caplog.records if hasattr(record, "recipients")]
    assert logged == [["h***g@gmail.com"]]
