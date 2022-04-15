import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pytest
from django.urls import reverse
from django.core import mail

# Create your tests here.
@pytest.fixture
def test_registerview_post_test(client):
    response = client.post(
        reverse('register'),
        {'email': 'redhohoho@naver.com', 'password': 'redhohoho', 'password_confirm': 'redhohoho', 'username': 'redhohoho', 'nickname': 'redhohoho', 'profile_image':''}
    )
    print("test!!!")
    assert response.status_code == 200


@pytest.fixture
def test_mail():
    subject = '회원가입을 축하드립니다.'
    message = '다음 주소로 이동하셔서 인증하세요.'
    result = mail.send_mail(subject, message, 'admin@devspoon.com', ['redhohoho@naver.com'])
    assert result == 1
