from .base import *
# from .sub_settings.debug.nose import * #NOSE coverage trace
# from .sub_settings.http.cors import *
from .sub_settings.system.logs import *

# from .sub_settings.oauth import *
from decouple import config

# import status checking
# import json
# print(json.dumps(DEFAULT_LOGGING, indent=4, sort_keys=True))

import mimetypes
mimetypes.add_type("application/javascript", ".js", True)

"""
export DJANGO_SETTINGS_MODULE=config.settings.dev
export DJANGO_SETTINGS_MODULE=config.settings.test
export DJANGO_SETTINGS_MODULE=config.settings.stage
export DJANGO_SETTINGS_MODULE=config.settings.prod
"""

DEBUG=config('DEBUG_STATE')

ALLOWED_HOSTS = [config('ALLOWED_HOSTS_IP')]

# debug toolbar를 동작시키기 위한 서버 ip 정보를 명시함
INTERNAL_IPS = [
    config('IP_ADDRESSES1'),config('IP_ADDRESSES2'),
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
    "debug_toolbar",
    "django_nose",
    "silk",
    'django_extensions',
]


# django-extentions로 ERP 만들때 해줘야 하는 설정
GRAPH_MODELS = {
    "all_applications": True,
    "group_models": True,
}

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
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

DATABASE_ROUTERS = ['core.replica_router.ReplicationRouter']

DATABASES = {
    # "default": {
    #     "ENGINE": "django.db.backends.sqlite3",
    #     "NAME": os.path.join(ROOT_DIR, "db.sqlite3"),
    # },
    "default": {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': config('DEFAULT_DB_HOST'),
        'PORT': config('DEFAULT_DB_PORT',default=3306, cast=int),
        'NAME': config('DEFAULT_DB_NAME'),
        'USER': config('DEFAULT_DB_USER'),
        'PASSWORD': config('DEFAULT_DB_PASSWORD'),
        'CHARSET': config('DEFAULT_DB_CHARSET'),
        # 'TEST': {
        #     'NAME': config('DEFAULT_DB_TEST_NAME)'
        # }
        # * 주의 TEST 파라미터는 데이터베이스 사용후 삭제함
     },
    'replica1': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': config('REPLICA1_DB_HOST'),
        'PORT': config('DEFAULT_DB_PORT',default=3306, cast=int),
        'NAME': config('REPLICA1_DB_NAME'),
        'USER': config('REPLICA1_DB_USER'),
        'PASSWORD': config('REPLICA1_DB_PASSWORD'),
        'CHARSET': config('REPLICA1_DB_CHARSET'),
        # 'TEST': {
        #     'NAME': config('REPLICA1_DB_TEST_NAME)'
        # }
        # * 주의 TEST 파라미터는 데이터베이스 사용후 삭제함
    },
}

AUTH_USER_MODEL = 'users.User'

# reference blog : https://velog.io/@kim6515516/Django-silk-%EC%84%B1%EB%8A%A5-%ED%94%84%EB%A1%9C%ED%8C%8C%EC%9D%BC%EB%9F%AC
# reference github : https://github.com/jazzband/django-silk

SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(ROOT_DIR, "media")

STATIC_URL = "/static/"
# STATIC_URL = "/assets/"
STATIC_DIR = os.path.join(ROOT_DIR, 'static')
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

