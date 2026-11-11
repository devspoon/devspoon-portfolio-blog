import pytest
from django.test import override_settings

from utils.email.backends import TimeoutSendgridBackend

pytestmark = pytest.mark.portfolio


@override_settings(SENDGRID_TIMEOUT=7)
def test_timeout_reaches_the_client_that_sends_mail():
    backend = TimeoutSendgridBackend(api_key="test-key")

    assert backend.sg.client.timeout == 7
    # send_messages()는 sg.client.mail.send.post()를 호출한다.
    # 하위 client는 속성 접근 시 새로 만들어지므로 실제 요청 경로까지 확인한다.
    assert backend.sg.client.mail.send.timeout == 7
