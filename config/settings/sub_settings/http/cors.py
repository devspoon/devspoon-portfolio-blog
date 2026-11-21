import os
import sys
from decouple import config

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from config.settings.base import INSTALLED_APPS, MIDDLEWARE

# python -m pip install django-cors-headers
"""
https://oen-blog.tistory.com/46
https://github.com/adamchainz/django-cors-headers

* CORS_ALLOWED_ORIGINS : Previously this setting was called CORS_ORIGIN_WHITELIST, which still works as an alias, with the new name taking precedence.
"""


INSTALLED_APPS.insert(0, "corsheaders")

domain_str = config("DOMAIN_NAME")

# Only the site's own origins may make credentialed cross-origin requests: allowing every origin together
# with CORS_ALLOW_CREDENTIALS let any website read responses with the visitor's cookies.
# DOMAIN_NAME may list bare hosts ("example.com") or full origins; bare hosts get https://.
CORS_ALLOWED_ORIGINS = [
    d if "://" in d else f"https://{d}" for d in (s.strip() for s in domain_str.split(",")) if d
]
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True


CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "POST", "PUT"]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")
