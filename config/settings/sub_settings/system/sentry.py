"""Sentry 이벤트 필터.

실제 장애와 스캐너 노이즈를 분리하기 위한 정책이다.
스캔 트래픽은 nginx와 BlockSuspiciousPathMiddleware가 이미 차단하고 있으므로,
그래도 Sentry까지 올라오는 이벤트는 잡음일 뿐 조사 가치가 없다.
"""

import re

from django.core.exceptions import DisallowedHost, SuspiciousOperation
from django.http import Http404

# Sentry로 보내지 않을 예외.
# - Http404: 존재하지 않는 URL 탐색. 애플리케이션 결함이 아니다.
# - DisallowedHost: 도메인이 아닌 IP 직결/랜덤 Host 헤더 스캔.
# - SuspiciousOperation: Django 보안 계층이 이미 차단한 요청.
IGNORED_EXCEPTIONS = (Http404, DisallowedHost, SuspiciousOperation)

# 서비스와 무관한 탐색성 경로. 여기서 발생한 이벤트는 원인이 스캐너로 확정된다.
# 미들웨어와 달리 여기서는 path가 아니라 전체 URL을 검사하므로 query/fragment
# 구분자(?, #)도 경로 끝으로 인정해야 한다.
NOISY_PATH_PATTERN = re.compile(
    r"(\.php([/?#]|$))"
    r"|((^|/)(wp-admin|wp-content|wp-includes)([/?#]|$))"
    r"|((^|/)\.(env|git|aws|ssh)([/?#]|$))",
    re.IGNORECASE,
)


def is_noisy_path(event) -> bool:
    url = (event.get("request") or {}).get("url") or ""
    return bool(NOISY_PATH_PATTERN.search(url))


def before_send(event, hint):
    """Sentry 전송 직전 훅. None을 반환하면 이벤트를 버린다."""
    exc_info = hint.get("exc_info")
    if exc_info and isinstance(exc_info[1], IGNORED_EXCEPTIONS):
        return None

    if is_noisy_path(event):
        return None

    return event
