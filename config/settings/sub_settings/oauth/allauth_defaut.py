import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from config.settings.base import INSTALLED_APPS, AUTHENTICATION_BACKENDS

INSTALLED_APPS += [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.auth0',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.kakao',
]

AUTHENTICATION_BACKENDS += [
    'allauth.account.auth_backends.AuthenticationBackend',
]

# All auth
SITE_ID = 2
LOGIN_REDIRECT_URL = 'index'
ACCOUNT_LOGOUT_REDIRECT_URL = 'index'
ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile', 'email'
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

SOCIALACCOUNT_ADAPTER = 'web.models.CustomSocialAccountAdapter'
ACCOUNT_UNIQUE_EMAIL = False