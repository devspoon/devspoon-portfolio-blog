from .base import *
# from .sub_settings.http.cors import *
from .sub_settings.system.logs import *


from decouple import config

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

DEBUG=config('DEBUG_STATE')

ALLOWED_HOSTS = [config('ALLOWED_HOSTS_IP')]

INSTALLED_APPS += [
    'django_prometheus',
]

'''
django_prometheus는 모든 middleware를 감싸는 형식으로
'django_prometheus.middleware.PrometheusBeforeMiddleware'는 최상단에
'django_prometheus.middleware.PrometheusAfterMiddleware'는 최하단에
정의한다
'''
MIDDLEWARE += []

MIDDLEWARE.insert(0,'django_prometheus.middleware.PrometheusBeforeMiddleware')
MIDDLEWARE.insert(-1,'django_prometheus.middleware.PrometheusAfterMiddleware')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
# STATIC_DIR = os.path.join(BASE_DIR, 'static')
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
