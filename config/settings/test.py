import mimetypes

from decouple import config
from django_redis import get_redis_connection

from .base import *
from .sub_settings.editor.summernote import *

# from .sub_settings.debug.nose import * #NOSE coverage trace
from .sub_settings.http.cors import *
from .sub_settings.oauth.allauth_default import *
from .sub_settings.system.logs import *

# from .sub_settings.oauth import *


# import status checking
# import json
# print(json.dumps(DEFAULT_LOGGING, indent=4, sort_keys=True))

mimetypes.add_type("application/javascript", ".js", True)

"""
export DJANGO_SETTINGS_MODULE=config.settings.dev
export DJANGO_SETTINGS_MODULE=config.settings.test
export DJANGO_SETTINGS_MODULE=config.settings.stage
export DJANGO_SETTINGS_MODULE=config.settings.prod
"""

# DEBUG = config("DEBUG_STATE")
DEBUG = False

host = config("ALLOWED_HOSTS_IP")

ALLOWED_HOSTS = host.split(",")

MIDDLEWARE += [
    "silk.middleware.SilkyMiddleware",
]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# Database multidatabase
# https://woolbro.tistory.com/82
# https://uiandwe.tistory.com/1252
# https://django-orm-cookbook-ko.readthedocs.io/en/latest/multiple_databases.html

# Databse Test Database setting, Multidatabase setting
# https://stackoverflow.com/questions/4650509/different-db-for-testing-in-django
# https://docs.djangoproject.com/en/4.0/topics/testing/overview/#the-test-database
# https://docs.djangoproject.com/en/4.0/topics/testing/advanced/#topics-testing-advanced-multidb

# pytest fixture with database
# https://djangostars.com/blog/django-pytest-testing/ # remove later

# replication
# https://docs.djangoproject.com/en/4.0/topics/db/multi-db/
# https://vixxcode.tistory.com/220
# https://koenwoortman.com/python-django-replication-database-router/
# https://andrewbrookins.com/python/scaling-django-with-postgres-read-replicas/
# https://sophilabs.com/blog/configure-a-read-replica-database-in-django
# https://urunimi.github.io/architecture/python/use-replica/

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://"
        + config("DEFAULT_CACHE_HOST")
        + ":"
        + config("DEFAULT_CACHE_PORT")
        + "/"
        + config("DEFAULT_CACHE_DATABASE"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "devspoon",
    }
}

INSTALLED_APPS += [
    "silk",
    "captcha",
]

REDIS_CONNECTION = get_redis_connection()

# Cache time to live is 15 minutes.
CACHE_TTL = 60 * 60 * 24
SESSION_ENGINE = "django.contrib.sessions.backends.cache"  # use only cache
SESSION_CACHE_ALIAS = "default"

AUTH_USER_MODEL = "users.User"

# reference blog : https://velog.io/@kim6515516/Django-silk-%EC%84%B1%EB%8A%A5-%ED%94%84%EB%A1%9C%ED%8C%8C%EC%9D%BC%EB%9F%AC
# reference github : https://github.com/jazzband/django-silk

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(ROOT_DIR, "media")

DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600

STATIC_URL = "/static/"
# STATIC_URL = "/assets/"
STATIC_DIR = os.path.join(ROOT_DIR, "static")
STATICFILES_DIRS = [
    STATIC_DIR,
]
# OR
# STATICFILES_DIRS = [
#     BASE_DIR / 'static'
# ]

# static url로 접근했을 때 연결되는 위치 정의
# static 파일을 한 곳에 모아서 서비스 할 경우 상위 STATICFILES_DIRS 변수는 불필요함

# STATIC_ROOT = os.path.join(ROOT_DIR, "static")

# Recaptcha Settings
RECAPTCHA_PUBLIC_KEY = config(
    "RECAPTCHA_PUBLIC_KEY", default="6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
)
RECAPTCHA_PRIVATE_KEY = config(
    "RECAPTCHA_PRIVATE_KEY", default="6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
)
# SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]
# RECAPTCHA_DOMAIN = "www.recaptcha.net"
