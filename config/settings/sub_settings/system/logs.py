import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from os.path import join

from config.settings.base import MIDDLEWARE, ROOT_DIR

MIDDLEWARE += [
    "request_logging.middleware.LoggingMiddleware",
]

"""
ref:
1. https://docs.djangoproject.com/en/4.0/topics/logging/#loggers
2. https://docs.djangoproject.com/en/4.0/howto/logging/#logging-how-to
3. https://docs.djangoproject.com/en/4.0/ref/logging/#logging-ref
4. https://wikidocs.net/77522
django에 정의된 로거를 사용할 경우 
패키지 설치를 먼저 해줘야 한다
예 ) pip install django-request-logging
- console - 콘솔에 로그를 출력한다. 로그 레벨이 INFO 이상이고 DEBUG=True일 때만 로그를 출력한다.
- django.server - python manage.py runserver로 작동하는 개발 서버에서만 사용하는 핸들러로 콘솔에 로그를 출력한다.
- mail_admins - 로그 내용을 이메일로 전송하는 핸들러로, 로그 레벨이 ERROR 이상이고 DEBUG=False 일때만 로그를 전송한다. 핸들러 사용 조건은 환경설정 파일에 ADMINS라는 항목을 추가하고 관리자 이메일을 등록해야 한다(예: ADMINS = ['admin@gmail.com']). 그리고 이메일 발송을 위한 SMTP 설정도 필요하다.
- 'propagate': False 설정은 해당 로거가 출력하는 로그를 기본 로거 django로 전달하지 않겠다는 의미로 True시 이중 출력된다
- 로그 레벨 
    1단계 DEBUG: 디버깅 목적으로 사용
    2단계 INFO: 일반 정보를 출력할 목적으로 사용
    3단계 WARNING: 경고 정보를 출력할 목적으로(작은 문제) 사용
    4단계 ERROR: 오류 정보를 출력할 목적으로(큰 문제) 사용
    5단계 CRITICAL: 아주 심각한 문제를 출력할 목적으로 사용
views에서 사용 예시
import logging
logger = logging.getLogger('django.server')
# 표현식
# https://developpaper.com/2-django-advanced-logging-function/
def home(request):
    logger.debug("debug!!!")
    # logger.info('info!!!')
    # logger.warning('warning!!!')
    # logger.error('error!!!')
    # logger.critical('critical!!!')
    return HttpResponse('finish')
issues : 윈도우 테스트시 debug level 출력 안됨, 파일 출력 안됨
         차후 버그 픽스
"""

# DEFAULT_LOGGING = {
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    # Filters
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    # Formatter
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] : {levelname} [{filename}:{name} -> {funcName} : {lineno}] {message}",
            "datefmt": "%d/%b/%Y %H:%M:%S",
            "style": "{",
        },
        "standard": {
            "format": "[%(asctime)s] %(levelname)s [%(filename)s:%(name)s -> %(funcName)5s() : %(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
    },
    # Handler
    "handlers": {
        "file": {
            "level": "DEBUG",
            "encoding": "utf-8",
            "class": "logging.handlers.RotatingFileHandler",
            "filters": ["require_debug_false"],
            "filename": join(ROOT_DIR, "logs/logfile.log"),
            "maxBytes": 1024 * 1024 * 15,
            "backupCount": 30,
            "formatter": "standard",
        },
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "django.server": {
            "level": "DEBUG",
            "filters": ["require_debug_true", "require_debug_false"],
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_true", "require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "formatter": "standard",
        },
    },
    # Logger
    "loggers": {
        "django": {
            "handlers": ["file", "console", "mail_admins"],
            "level": "WARNING",
        },
        # # runserver 작업시 콘솔 출력
        "django.server": {
            "handlers": ["django.server"],
            "level": "DEBUG",
            "propagate": False,
        },
        # 요청 출력
        "django.request": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        "common": {
            "handlers": [
                "console",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
        "home": {
            "handlers": [
                "console",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
        "blog": {
            "handlers": [
                "console",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
        "board": {
            "handlers": [
                "console",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
        "portfolio": {
            "handlers": [
                "console",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
        "users": {
            "handlers": [
                "console",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

COMMON_LOGGER = "common"
HOME_LOGGER = "home"
BLOG_LOGGER = "blog"
BOARD_LOGGER = "board"
PORTFOLIO_LOGGER = "portfolio"
USERS_LOGGER = "users"
