from django.conf import settings
from sendgrid_backend import SendgridBackend


class TimeoutSendgridBackend(SendgridBackend):
    """HTTP timeout을 적용한 SendGrid 백엔드.

    django-sendgrid-v5는 python-http-client에 timeout을 넘기지 않아, SendGrid가
    응답하지 않으면 발송이 무한 대기한다. 문의 폼은 동기 발송이라 worker까지 묶인다.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 하위 client(mail.send 등)는 생성될 때 이 값을 복사한다.
        self.sg.client.timeout = getattr(settings, "SENDGRID_TIMEOUT", 10)
