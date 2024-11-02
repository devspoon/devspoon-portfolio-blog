import random
import string
import threading
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail as sendmail

# 로거 설정
logger = logging.getLogger(__name__)


class EmailThread(threading.Thread):
    def __init__(
        self, subject, message, from_email, recipient_list, html, fail_silently
    ):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        self.fail_silently = fail_silently
        self.html = html
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMultiAlternatives(
            self.subject, self.message, self.from_email, to=self.recipient_list
        )
        if self.html:
            msg.attach_alternative(self.html, "text/html")
        
        try:
            # 이메일 전송 시도
            result = msg.send(self.fail_silently)
            # 전송 결과 로그 기록
            if result > 0:
                logger.info(f"Email sent successfully to {self.recipient_list}.")
            else:
                logger.warning(f"Email not sent to {self.recipient_list}. No recipients were successfully sent.")
        except Exception as e:
            # 예외 발생 시 로그 기록
            logger.error(f"Error sending email to {self.recipient_list}: {e}")


def send_mail(
    subject,
    recipient_list,
    *args,
    message,
    from_email=settings.EMAIL_HOST_USER,
    html_message=None,
    fail_silently=False,
    **kwargs
):
    EmailThread(
        subject, message, from_email, recipient_list, html_message, fail_silently
    ).start()
