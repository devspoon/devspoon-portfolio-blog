import pytest
from django.http import HttpResponse
from django.test import override_settings
from custom_middlewares.middlewares.access_guard import (
    BlockSuspiciousPathMiddleware,
)
from custom_middlewares.models import (
    ConnectionHardwareStats,
    ConnectionMethodStats,
)

HEADERS = {
    "HTTP_USER_AGENT": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    )
}

# home:index는 sqlite에서 union+slice 조합 때문에 쓸 수 없다(home.tests.test_home_html 참고).
NORMAL_URL = "/portfolio/"

# Sentry에 실제로 기록된 스캔 경로들
SUSPICIOUS_PATHS = [
    "/wp.php",
    "/site/phpinfo.php",
    "/public_html/phpinfo.php",
    "/wp-admin/phpinfo.php",
    "/includes/phpinfo.php",
    "/bbs/board.php",
    "/xmlrpc.php",
    "/wp-login.php",
    "/wp-content/uploads/shell.php",
    "/WP-ADMIN/",
    "/.env",
]


@pytest.mark.middlewares
@pytest.mark.django_db
@pytest.mark.parametrize("path", SUSPICIOUS_PATHS)
def test_suspicious_path_is_blocked_early(client, path):
    response = client.get(path, **HEADERS)

    assert response.status_code == 404
    # 조기 차단은 본문 없이 끝난다. URL resolver까지 갔다면 404 에러 페이지가 렌더된다.
    assert response.content == b""


@pytest.mark.middlewares
@pytest.mark.django_db
def test_blocked_path_does_not_touch_statistics(client):
    client.get("/bbs/board.php?bo_table=free&wr_id=1718", **HEADERS)

    assert ConnectionMethodStats.objects.count() == 0
    assert ConnectionHardwareStats.objects.count() == 0


@pytest.mark.middlewares
@pytest.mark.django_db
def test_normal_path_is_not_blocked(client):
    response = client.get(NORMAL_URL, **HEADERS)

    assert response.status_code == 200


@pytest.mark.middlewares
@pytest.mark.django_db
def test_unknown_normal_path_still_renders_error_page(client):
    """차단 대상이 아닌 오탈자 URL은 기존 404 페이지를 유지한다."""
    response = client.get("/does-not-exist.html", **HEADERS)

    assert response.status_code == 404
    assert b"404 Error" in response.content


@pytest.mark.middlewares
@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/portfolio/",
        "/blog/",
        "/board/",
        "/users/login/",
        "/static/css/style.css",
        "/phpinfo",  # 확장자 없는 경로는 차단 대상이 아니다
        "/blog/phpstorm-review/",
    ],
)
def test_service_paths_are_not_suspicious(path):
    middleware = BlockSuspiciousPathMiddleware(lambda request: HttpResponse())

    assert middleware.is_suspicious_path(path) is False


@pytest.mark.middlewares
@override_settings(BLOCK_SUSPICIOUS_PATHS=False)
def test_guard_can_be_disabled(rf):
    sentinel = HttpResponse(status=200)
    middleware = BlockSuspiciousPathMiddleware(lambda request: sentinel)

    assert middleware(rf.get("/wp.php")) is sentinel


@pytest.mark.middlewares
@override_settings(SUSPICIOUS_PATH_RESPONSE_STATUS=403)
def test_block_status_is_configurable(rf):
    middleware = BlockSuspiciousPathMiddleware(lambda request: HttpResponse())

    assert middleware(rf.get("/wp.php")).status_code == 403


@pytest.mark.middlewares
@override_settings(SUSPICIOUS_PATH_PATTERNS=[r"^/blocked/"])
def test_patterns_are_configurable(rf):
    middleware = BlockSuspiciousPathMiddleware(lambda request: HttpResponse())

    assert middleware.is_suspicious_path("/blocked/here") is True
    assert middleware.is_suspicious_path("/wp.php") is False
