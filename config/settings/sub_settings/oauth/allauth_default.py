import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from config.settings.base import INSTALLED_APPS, AUTHENTICATION_BACKENDS

# All auth
# https://django-allauth.readthedocs.io/en/latest/

# google api setting : https://console.developers.google.com/
# kakao api setting : https://developers.kakao.com/
# naver api setting : https://developers.naver.com/

# admin setting
# 

INSTALLED_APPS += [
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.auth0',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.kakao',
    'allauth.socialaccount.providers.naver',
]

AUTHENTICATION_BACKENDS += [
    'allauth.account.auth_backends.AuthenticationBackend',
]

# All auth
# app에 sites 추가 후 admin으로 접속하여 sites 메뉴에 도메인을 입력함
# 입력 폼의 링크에 보이는 숫자가 site id임
# 예) http://localhost:8000/admin/sites/site/1/change/ -> site id = 1
# 해당 정보는 각 서비스 api 등록시 입력한 "승인된 리디렉션 uri" 주소에 사용됨
# 이후 social applications에 연동할 서비스 정보 추가
# 구글의 경우  client id, secret key, sites 선택 을 입력 및 선택해준다

# 해당 로그인으로 가져오는 정보 중 email은 user의 email 정보와 중복이 되어 
# 기존 가입자의 경우 메일의 유일성이 사라짐
# 구글의 꼼수로 아이디 뒤에 + 문자를 입력하면 + 이후는 무시한다

# http://127.0.0.1:8000/oauth/<service>/login/callback/
# 예 ) http://127.0.0.1:8000/oauth/kakao/login/callback/


SITE_ID = 1
LOGIN_REDIRECT_URL = 'blog:index'
ACCOUNT_LOGOUT_REDIRECT_URL = 'blog:index'

# logout을 url, get으로 접근해도 처리를 수행할 수 있게 설정
ACCOUNT_LOGOUT_ON_GET = True

# 기본적으로 소셜 로그인시 특정 화면을 한번 거쳐가게 되어 있음
# SOCIALACCOUNT_LOGIN_ON_GET 값을 True로 하면 바로 구글 로그인 페이지 부터 시작함
SOCIALACCOUNT_LOGIN_ON_GET = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile', 'email'
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
}

# 카카오 로그인 설정
# 앱키의 reset api 키를 인증 키로 사용함
# 이메일이 선택 동의이기에 정보가 안올 수 있음
# 필수로 받으려면 설정의 필수동의를 위해 비즈니스 정보의 비즈 앱 정보를 만든다

# 소셜 로그인 할때마다 메일을 보내는 기본 기능을 끔 (메일 정보가 없을 수 있는 경우 대비)
ACCOUNT_EMAIL_REQUIRED = False

# 확인 메일이 반복해서 전송되는 기능을 끔
ACCOUNT_EMAIL_VERIFICATION = 'none'

SOCIALACCOUNT_ADAPTER = 'users.models.CustomSocialAccountAdapter'
ACCOUNT_UNIQUE_EMAIL = False