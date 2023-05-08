import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from  config.settings.base import INSTALLED_APPS, MIDDLEWARE

# python -m pip install django-cors-headers
'''
https://oen-blog.tistory.com/46
https://github.com/adamchainz/django-cors-headers

* CORS_ALLOWED_ORIGINS : Previously this setting was called CORS_ORIGIN_WHITELIST, which still works as an alias, with the new name taking precedence.
'''


INSTALLED_APPS.insert(0,"corsheaders")

CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True


CORS_ALLOW_METHODS = [
    'DELETE', 'GET', 'OPTIONS', 'POST', 'PUT'
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

MIDDLEWARE.insert(0,"corsheaders.middleware.CorsMiddleware")

