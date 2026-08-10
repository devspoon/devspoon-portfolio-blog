from unittest import mock

import pytest
from django.core import mail

from utils.email.async_send_email import EmailThread, send_mail

pytestmark = pytest.mark.portfolio

# 회원가입 인증 메일(utils/email/verify_email_mixins.py)이 쓰는 경로다.
# 문의 폼은 send_mail_sync를 쓰지만 이 경로는 그대로 남아 있으므로 함께 검증한다.


def test_email_thread_sends_and_records_the_result():
    thread = EmailThread(
        "hello",
        "body",
        "admin@devspoon.com",
        ["user@devspoon.com"],
        "<p>body</p>",
        False,
    )

    thread.start()
    thread.join(timeout=5)

    assert thread.result is True
    assert len(mail.outbox) == 1
    assert mail.outbox[0].alternatives == [("<p>body</p>", "text/html")]


def test_email_thread_records_failure_without_raising():
    with mock.patch(
        "django.core.mail.EmailMultiAlternatives.send",
        side_effect=Exception("HTTP Error 401: Unauthorized"),
    ):
        thread = EmailThread(
            "hello", "body", "admin@devspoon.com", ["user@devspoon.com"], None, False
        )
        thread.start()
        thread.join(timeout=5)

    assert thread.result is False


def test_send_mail_starts_a_thread_and_returns_immediately():
    with mock.patch(
        "utils.email.async_send_email.EmailThread"
    ) as thread_class:
        result = send_mail(
            subject="hello",
            recipient_list=["user@devspoon.com"],
            message="body",
            from_email="admin@devspoon.com",
        )

    assert result is None
    thread_class.return_value.start.assert_called_once()


def test_plain_text_message_has_no_html_alternative():
    thread = EmailThread(
        "hello", "body", "admin@devspoon.com", ["user@devspoon.com"], None, False
    )

    thread.start()
    thread.join(timeout=5)

    assert mail.outbox[0].alternatives == []
