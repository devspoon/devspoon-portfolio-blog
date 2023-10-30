import mimetypes
from .base import *
from django_redis import get_redis_connection
from .sub_settings.editor.summernote import *

# from .sub_settings.http.cors import *
from .sub_settings.system.logs import *
from .sub_settings.http.cors import *
from .sub_settings.oauth.allauth_default import *
from .sub_settings.system.logs import *

from decouple import config

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

mimetypes.add_type("application/javascript", ".js", True)

"""
export DJANGO_SETTINGS_MODULE=config.settings.dev
export DJANGO_SETTINGS_MODULE=config.settings.test
export DJANGO_SETTINGS_MODULE=config.settings.stage
export DJANGO_SETTINGS_MODULE=config.settings.prod
"""

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

DEBUG = False

host = config("ALLOWED_HOSTS_IP")

ALLOWED_HOSTS = host.split(",")

DATABASE_ROUTERS = ["core.replica_router.ReplicationRouter"]

DATABASES = {
    # "default": {
    #     "ENGINE": "django.db.backends.sqlite3",
    #     "NAME": os.path.join(ROOT_DIR, "db.sqlite3"),
    # },
    "default": {
        "ENGINE": config("DEFAULT_DB_ENGINE", default="django.db.backends.mysql"),
        "HOST": config("DEFAULT_DB_HOST"),
        "PORT": config("DEFAULT_DB_PORT", default=3306, cast=int),
        "NAME": config("DEFAULT_DB_NAME"),
        "USER": config("DEFAULT_DB_USER"),
        "PASSWORD": config("DEFAULT_DB_PASSWORD"),
        "CHARSET": config("DEFAULT_DB_CHARSET", default="utf8mb4"),
        "OPTIONS": {"options": config("DEFAULT_DB_OPTIONS", default="")},
        "CONN_MAX_AGE": config("DEFAULT_DB_CONN_MAX_AGE", cast=int),
    },
    "replica1": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": config("REPLICA1_DB_HOST"),
        "PORT": config("REPLICA1_DB_PORT", default=3306, cast=int),
        "NAME": config("REPLICA1_DB_NAME"),
        "USER": config("REPLICA1_DB_USER"),
        "PASSWORD": config("REPLICA1_DB_PASSWORD"),
        "CHARSET": config("REPLICA1_DB_CHARSET", default="utf8mb4"),
        "OPTIONS": {"options": config("REPLICA1_DB_OPTIONS", default="")},
        "CONN_MAX_AGE": config("REPLICA1_DB_CONN_MAX_AGE", cast=int),
    },
}


INSTALLED_APPS += []

"""
django_prometheus는 모든 middleware를 감싸는 형식으로
'django_prometheus.middleware.PrometheusBeforeMiddleware'는 최상단에
'django_prometheus.middleware.PrometheusAfterMiddleware'는 최하단에
정의한다
"""
MIDDLEWARE += []

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

REDIS_CONNECTION = get_redis_connection()

CACHE_TTL = 60 * 60 * 24
SESSION_ENGINE = "django.contrib.sessions.backends.cache"  # use only cache
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

AUTH_USER_MODEL = "users.User"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_DIR = os.path.join(ROOT_DIR, "static")
# STATICFILES_DIRS = [
#     STATIC_DIR,
# ]
# OR
# STATICFILES_DIRS = [
#     BASE_DIR / 'static'
# ]

# static url로 접근했을 때 연결되는 위치 정의
# static 파일을 한 곳에 모아서 서비스 할 경우 상위 STATICFILES_DIRS 변수는 불필요함

STATIC_ROOT = os.path.join(ROOT_DIR, "static")

# python manage.py collectstatic

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(ROOT_DIR, "media")

DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600

trusted_domain_list = config("CSRF_TRUSTED_ORIGINS")

CSRF_TRUSTED_ORIGINS = trusted_domain_list.split(",")

sentry_sdk.init(
    dsn=config("SENTRY_DNS"),
    integrations=[
        DjangoIntegration(),
    ],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)

# Recaptcha Settings
RECAPTCHA_PUBLIC_KEY = config(
    "RECAPTCHA_PUBLIC_KEY", default="6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
)
RECAPTCHA_PRIVATE_KEY = config(
    "RECAPTCHA_PRIVATE_KEY", default="6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
)
# SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]
# RECAPTCHA_DOMAIN = 'www.recaptcha.net'
