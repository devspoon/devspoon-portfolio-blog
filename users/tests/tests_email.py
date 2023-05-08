import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pytest
from django.core import mail
from django.urls import reverse


# Create your tests here.
@pytest.fixture
def test_register_post(client):
    response = client.post(
        reverse("register"),
        {
            "email": "test@gmail.com",
            "password": "test1324",
            "password_confirm": "test1324",
            "username": "test",
            "nickname": "test",
            "profile_image": "",
        },
    )
    assert response.status_code == 200


@pytest.fixture
def test_mail():
    subject = "Congratulations on becoming a member."
    message = "Go to the following address and verify."
    result = mail.send_mail(
        subject,
        message,
        "admin@gmail.com",
        [
            "test@gmail.com",
        ],
    )
    assert result == 1
