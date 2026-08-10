import pytest
from django.urls import reverse

from common.error.error_views import (
    bad_request_page,
    page_not_found_page,
    permission_denied_page,
    server_error_page,
)

# 에러 템플릿이 공통 base를 상속해 사이트 정보를 조회하므로 DB 접근이 필요하다.
pytestmark = [pytest.mark.http_error, pytest.mark.django_db]

HANDLERS = [
    (bad_request_page, 400),
    (permission_denied_page, 403),
    (page_not_found_page, 404),
    (server_error_page, 500),
]


@pytest.mark.parametrize("handler,expected_status", HANDLERS)
def test_error_handlers_return_their_status(rf, handler, expected_status):
    """이전 구현은 status_code를 세팅한 응답을 버리고 render()의 200을 반환했다."""
    response = handler(rf.get("/boom"))

    assert response.status_code == expected_status


@pytest.mark.parametrize("handler,expected_status", HANDLERS)
def test_error_handlers_render_the_status_in_the_page(
    rf, handler, expected_status
):
    response = handler(rf.get("/boom"))

    assert str(expected_status).encode() in response.content


@pytest.mark.django_db
def test_csrf_failure_redirects_home(rf):
    from common.error.error_views import csrf_failure

    response = csrf_failure(rf.post("/portfolio/mail"), reason="no token")

    assert response.status_code == 302
    assert response.url == reverse("home:index")


@pytest.mark.django_db
def test_unknown_url_answers_404_end_to_end(client):
    """handler404를 거친 실제 응답도 404여야 한다."""
    response = client.get("/no-such-page-here/")

    assert response.status_code == 404
    assert b"404 Error" in response.content
