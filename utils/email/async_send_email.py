import logging
import threading

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

# 로거 설정
logger = logging.getLogger(__name__)


def mask_email(address: str) -> str:
    """로그/Sentry에 원문 이메일이 남지 않도록 local part를 가린다."""
    address = str(address or "")
    if "@" not in address:
        return "***"

    local, domain = address.rsplit("@", 1)
    if len(local) <= 2:
        masked_local = (local[0] + "*") if local else "*"
    else:
        masked_local = f"{local[0]}***{local[-1]}"

    return f"{masked_local}@{domain}"


def mask_recipients(recipient_list) -> list:
    if not recipient_list:
        return []
    return [mask_email(address) for address in recipient_list]


def build_message(subject, message, from_email, recipient_list, html):
    msg = EmailMultiAlternatives(
        subject, message, from_email, to=recipient_list
    )
    if html:
        msg.attach_alternative(html, "text/html")
    return msg


def send_mail_sync(
    subject,
    recipient_list,
    *args,
    message,
    from_email=settings.EMAIL_HOST_USER,
    html_message=None,
    fail_silently=False,
    **kwargs,
) -> bool:
    """메일을 동기로 발송하고 성공 여부를 반환한다.

    호출자가 발송 결과에 따라 사용자 안내와 상태 저장을 분리할 수 있도록,
    예외를 삼키지 않고 bool로 정규화해 돌려준다.
    """
    masked = mask_recipients(recipient_list)
    msg = build_message(
        subject, message, from_email, recipient_list, html_message
    )

    try:
        sent_count = msg.send(fail_silently)
    except Exception as error:
        # 메일 벤더 인증/크레딧 문제 등 외부 요인이 대부분이다.
        logger.error(
            "Error sending email",
            extra={"recipients": masked, "error": str(error)},
        )
        return False

    if sent_count > 0:
        logger.info("Email sent successfully", extra={"recipients": masked})
        return True

    logger.warning(
        "Email not sent. No recipients were successfully sent.",
        extra={"recipients": masked},
    )
    return False


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
        self.result = None
        threading.Thread.__init__(self)

    def run(self):
        self.result = send_mail_sync(
            subject=self.subject,
            recipient_list=self.recipient_list,
            message=self.message,
            from_email=self.from_email,
            html_message=self.html,
            fail_silently=self.fail_silently,
        )


def send_mail(
    subject,
    recipient_list,
    *args,
    message,
    from_email=settings.EMAIL_HOST_USER,
    html_message=None,
    fail_silently=False,
    **kwargs,
):
    """메일을 백그라운드 스레드로 발송한다.

    호출자는 발송 결과를 알 수 없다. 결과가 필요하면 send_mail_sync를 쓴다.
    """
    EmailThread(
        subject, message, from_email, recipient_list, html_message, fail_silently
    ).start()
