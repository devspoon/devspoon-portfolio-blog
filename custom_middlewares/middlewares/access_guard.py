import logging
import re

from django.conf import settings
from django.http import HttpResponse

logger = logging.getLogger(getattr(settings, "COMMON_LOGGER", "django"))

"""
nginx에서 1차로 끊지 못한 비서비스 요청을 애플리케이션 초입에서 2차로 차단한다.
이 미들웨어는 nginx 차단 설정의 대체물이 아니라 fallback이다.

- 이 서비스는 PHP를 실행하지 않으므로 `.php` 계열 요청은 전부 탐색성 트래픽이다.
- 통계 미들웨어보다 앞에 두어야 차단 요청이 통계 DB write 경로를 타지 않는다.
- Django는 nginx의 `return 444`처럼 연결을 즉시 drop할 수 없으므로 조기 404를 반환한다.
"""

DEFAULT_SUSPICIOUS_PATH_PATTERNS = [
    # WordPress 관리자/리소스 디렉터리 탐색
    r"(^|/)(wp-admin|wp-content|wp-includes)(/|$)",
    # 잘 알려진 WordPress/PHP 진입점
    r"(^|/)(phpinfo|xmlrpc|wp-login|wp-config|wp-cron|wp-load|wp-mail"
    r"|wp-settings|wp-signup|wp-trackback|wp)\.php$",
    # 나머지 모든 .php 요청. 이 서비스는 PHP를 실행하지 않는다.
    r"\.php(?:/|$)",
    # 설정/자격증명 파일 유출 스캔
    r"(^|/)\.(env|git|aws|ssh)(/|$)",
]


class BlockSuspiciousPathMiddleware:
    """서비스와 무관한 탐색성 경로를 URL resolver 이전에 차단한다."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, "BLOCK_SUSPICIOUS_PATHS", True)
        self.status = getattr(settings, "SUSPICIOUS_PATH_RESPONSE_STATUS", 404)
        # 차단은 정상 동작이라 기본은 INFO다. 다만 COMMON_LOGGER는 WARNING이라
        # 기본 설정에서는 기록되지 않는다. 차단량을 로그로 집계해야 할 때
        # 이 값을 "WARNING"으로 올린다.
        self.log_level = logging.getLevelName(
            getattr(settings, "SUSPICIOUS_PATH_LOG_LEVEL", "INFO")
        )
        raw_patterns = getattr(
            settings,
            "SUSPICIOUS_PATH_PATTERNS",
            DEFAULT_SUSPICIOUS_PATH_PATTERNS,
        )
        self.patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in raw_patterns
        ]

    def __call__(self, request):
        if self.enabled and self.is_suspicious_path(request.path_info):
            logger.log(
                self.log_level,
                "blocked suspicious path %s %s -> %s",
                request.method,
                request.path_info,
                self.status,
                extra={
                    "path": request.path_info,
                    "method": request.method,
                    "status": self.status,
                },
            )
            return HttpResponse(status=self.status)

        return self.get_response(request)

    def is_suspicious_path(self, path: str) -> bool:
        return any(pattern.search(path) for pattern in self.patterns)
