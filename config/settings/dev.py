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


DEBUG = config("DEBUG_STATE") == "True"

host = config("ALLOWED_HOSTS_IP")

ALLOWED_HOSTS = host.split(",")

# debug toolbar를 동작시키기 위한 서버 ip 정보를 명시함
INTERNAL_IPS = [
    config("IP_ADDRESSES1"),
    config("IP_ADDRESSES2"),
]

if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]

    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        # "silk.middleware.SilkyMiddleware",
    ]

    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ]


def custom_show_toolbar(self):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
    "ENABLE_STACKTRACES": True,
    "SHOW_TOOLBAR_CALLBACK": custom_show_toolbar,
}

INSTALLED_APPS += [
    # "silk",
    "django_extensions",
]

# django-extentions로 ERP 만들때 해줘야 하는 설정
GRAPH_MODELS = {
    "all_applications": True,
    "group_models": True,
}


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

DATABASE_ROUTERS = ["core.replica_router.ReplicationRouter"]

DATABASES = {
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
        "ENGINE": config("REPLICA1_DB_ENGINE", default="django.db.backends.mysql"),
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

# Cache time to live is 15 minutes.
CACHE_TTL = 60 * 60 * 24
SESSION_ENGINE = "django.contrib.sessions.backends.cache"  # use only cache
SESSION_CACHE_ALIAS = "default"

AUTH_USER_MODEL = "users.User"

# reference blog : https://velog.io/@kim6515516/Django-silk-%EC%84%B1%EB%8A%A5-%ED%94%84%EB%A1%9C%ED%8C%8C%EC%9D%BC%EB%9F%AC
# reference github : https://github.com/jazzband/django-silk

SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = False

SILKY_META = True

# SILKY_AUTHENTICATION = True  # User must login
# SILKY_AUTHORISATION = True  # User must have permissions

# SILKY_MAX_REQUEST_BODY_SIZE = -1  # Silk takes anything <0 as no limit
# SILKY_MAX_RESPONSE_BODY_SIZE = 1024  # If response body>1024 bytes, ignore

# If this is not set, MEDIA_ROOT will be used.
# SILKY_PYTHON_PROFILER_RESULT_PATH = '/path/to/profiles/'
SILKY_PYTHON_PROFILER_EXTENDED_FILE_NAME = True

# SILKY_INTERCEPT_PERCENT = 50 # log only 50% of requests

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(ROOT_DIR, "media")

DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600

STATIC_URL = "/static/"
# STATIC_URL = "/assets/"
# STATIC_ROOT = os.path.join(ROOT_DIR, "static")
STATIC_DIR = os.path.join(ROOT_DIR, "static")
STATICFILES_DIRS = [
    os.path.join(ROOT_DIR, "static"),
]
# # OR
# STATICFILES_DIRS = [
#     BASE_DIR / 'static'
# ]

# STATIC_ROOT = os.path.join(ROOT_DIR, "static")

# static url로 접근했을 때 연결되는 위치 정의
# static 파일을 한 곳에 모아서 서비스 할 경우 상위 STATICFILES_DIRS 변수는 불필요함


NOTEBOOK_ARGUMENTS = [
    "--ip",
    "127.0.0.1",
    "--port",
    "8888",
    "--allow-root",  # root 권한 사용 경고를 무시합니다.
    # "--no-browser", # 노트북 서버만 실행합니다.
    "--NotebookApp.token=''",
    "--NotebookApp.password=''",
    # 위 옵션은 노트북에 접근할 때 Token 또는 Password가 필요 없도록 합니다.
]
