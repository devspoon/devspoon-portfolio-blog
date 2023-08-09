"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from os.path import join
from pathlib import Path

# linux requirement
import pymysql
from decouple import config
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

# from .sub_settings.email.sendinblue import *
# from .sub_settings.email.mailgun import *
from .sub_settings.email.sendgrid import *

# from .sub_settings.email.aws_ses import *


pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = os.path.dirname(BASE_DIR)
TEMPLATE_DIR = os.path.join(ROOT_DIR, "templates")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "home",
    "users",
    "blog",
    "board",
    "portfolio",
    "custom_middlewares",
    "mptt",
    "anymail",
    "imagekit",
    "rangefilter",
    "django_user_agents",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
    "custom_middlewares.common.statistics.ConnectionMethodStatsMiddleware",
    "custom_middlewares.common.statistics.ConnectionHardwareStatsMiddleware",
]

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]  # 기본 인증 백엔드

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

# LANGUAGE_CODE = "ko-kr"
LANGUAGE_CODE = "en-us"

# TIME_ZONE = "Asia/Seoul"
TIME_ZONE = "UTC"

USE_I18N = True

LANGUAGES = [
    ("ko", _("Korean")),
    ("en", _("English")),
]

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

USE_TZ = True  # true로 선택하면 UTC 기준으로 시간이 저장됨
# ref : https://it-eldorado.tistory.com/13

# 자동으로 모델의 id 혹은 pk를 설정해줌
# ref :
# 1. https://dev.to/weplayinternet/upgrading-to-django-3-2-and-fixing-defaultautofield-warnings-518n
# 2. https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 기본 로그인 페이지 URL 지정
# login_required 장식자 등에 의해서 사용
LOGIN_URL = "/users/login/"

# 로그인 완료 후 next 인자가 지정되면 해당 URL 페이지로 이동
# next 인자가 없으면 아래 URL로 이동

LOGIN_REDIRECT_URL = "home:index"

# 로그아웃 후에 next 인자기 지정되면 해당 URL 페이지로 이동
# next 인자가 없으면 LOGOUT_REDIRECT_URL로 이동
# LOGOUT_REDIRECT_URL이 None(디폴트)이면, 'registration/logged_out.html' 템플릿 렌더링
LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL

# 인증에 사용할 커스텀 User 모델 지정 : '앱이름.모델명'
# AUTH_USER_MODEL = 'user.Usert'

SITE_ID = 1

# messages setting
MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}


# Django Session Timeout Code
# SESSION_COOKIE_AGE = 1200 # second
SESSION_COOKIE_AGE = 2147483647
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# SESSION_COOKIE_SECURE = True # https

# django-user-agent의 캐시 사용하려는 경우 'default'로 설정, 그외에는 None으로 설정
USER_AGENTS_CACHE = "default"

PASSWORD_REPLACEMENT_CYCLE = 6

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
