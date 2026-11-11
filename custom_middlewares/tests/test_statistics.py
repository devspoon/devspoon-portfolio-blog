from unittest import mock

import pytest
from django.db import DatabaseError, IntegrityError, transaction
from django.utils import timezone

from custom_middlewares.middlewares.statistics import (
    ConnectionHardwareStatsMiddleware,
    ConnectionMethodStatsMiddleware,
    increment_daily_counter,
)
from custom_middlewares.models import (
    ConnectionHardwareStats,
    ConnectionMethodStats,
)

WINDOWS_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
)
HEADERS = {"HTTP_USER_AGENT": WINDOWS_UA}

# home:index는 sqlite에서 union+slice 조합 때문에 쓸 수 없다(home.tests.test_home_html 참고).
NORMAL_URL = "/portfolio/"

pytestmark = pytest.mark.middlewares


@pytest.mark.django_db
def test_increment_creates_single_row_for_today():
    increment_daily_counter(ConnectionMethodStats, "win")

    stats = ConnectionMethodStats.objects.get()
    assert stats.stat_date == timezone.localdate()
    assert stats.win == 1


@pytest.mark.django_db
def test_repeated_increments_reuse_the_same_row():
    for _ in range(5):
        increment_daily_counter(ConnectionMethodStats, "win")
    increment_daily_counter(ConnectionMethodStats, "mac")

    assert ConnectionMethodStats.objects.count() == 1
    stats = ConnectionMethodStats.objects.get()
    assert stats.win == 5
    assert stats.mac == 1


@pytest.mark.django_db
def test_stat_date_unique_constraint_blocks_duplicates():
    today = timezone.localdate()
    ConnectionMethodStats.objects.create(stat_date=today)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            ConnectionMethodStats.objects.create(stat_date=today)


@pytest.mark.django_db
def test_increment_recovers_from_concurrent_create():
    """다른 요청이 오늘 row를 먼저 만든 경합 상황을 재현한다.

    이전 구현은 이 상황에서 같은 날짜 row가 하나 더 생겼고, 그 뒤로는 모든 요청이
    MultipleObjectsReturned로 실패했다.
    """
    today = timezone.localdate()
    ConnectionMethodStats.objects.create(stat_date=today, win=5)

    real_filter = ConnectionMethodStats.objects.filter
    call_count = []

    def first_update_finds_nothing(*args, **kwargs):
        call_count.append(1)
        if len(call_count) == 1:
            # 첫 UPDATE 시점에는 오늘 row가 아직 없었다고 가정한다.
            return real_filter(pk=0)
        return real_filter(*args, **kwargs)

    with mock.patch.object(
        ConnectionMethodStats.objects, "filter", first_update_finds_nothing
    ), mock.patch.object(
        ConnectionMethodStats.objects,
        "create",
        mock.Mock(side_effect=IntegrityError("duplicate stat_date")),
    ):
        increment_daily_counter(ConnectionMethodStats, "win")

    assert ConnectionMethodStats.objects.count() == 1
    assert ConnectionMethodStats.objects.get().win == 6


@pytest.mark.parametrize(
    "user_agent,expected",
    [
        (WINDOWS_UA, "win"),
        ("Mozilla/5.0 (Macintosh; Intel mac OS X 10_15_7)", "mac"),
        ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)", "iph"),
        ("Mozilla/5.0 (Linux; Android 14; Pixel 8)", "android"),
        ("ClaudeBot/1.0", "oth"),
    ],
)
def test_method_field_resolution(user_agent, expected):
    assert ConnectionMethodStatsMiddleware.resolve_field(user_agent) == expected


@pytest.mark.django_db
def test_request_records_both_statistics(client):
    client.get(NORMAL_URL, **HEADERS)

    assert ConnectionMethodStats.objects.get().win == 1
    assert ConnectionHardwareStats.objects.get().pc == 1


@pytest.mark.django_db
def test_repeated_requests_do_not_duplicate_rows(client):
    for _ in range(3):
        client.get(NORMAL_URL, **HEADERS)

    assert ConnectionMethodStats.objects.count() == 1
    assert ConnectionHardwareStats.objects.count() == 1
    assert ConnectionMethodStats.objects.get().win == 3


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path", ["/admin/", "/static/css/style.css", "/robots.txt", "/sitemap.xml"]
)
def test_excluded_paths_are_not_counted(client, path):
    client.get(path, **HEADERS)

    assert ConnectionMethodStats.objects.count() == 0
    assert ConnectionHardwareStats.objects.count() == 0


@pytest.mark.django_db
def test_path_containing_admin_is_still_counted(client):
    """이전 구현은 'admin' 부분 문자열만 보고 정상 URL까지 통계에서 제외했다."""
    client.get("/blog/django-admin-tips/", **HEADERS)

    assert ConnectionMethodStats.objects.count() == 1


@pytest.mark.django_db
def test_database_error_does_not_break_the_request(client):
    with mock.patch(
        "custom_middlewares.middlewares.statistics.increment_daily_counter",
        side_effect=DatabaseError("stats table is unavailable"),
    ):
        response = client.get(NORMAL_URL, **HEADERS)

    assert response.status_code == 200


@pytest.mark.parametrize(
    "flags,expected",
    [
        ({"is_mobile": True}, "mobile"),
        ({"is_tablet": True}, "tablet"),
        ({"is_pc": True}, "pc"),
        ({"is_bot": True}, "bot"),
    ],
)
def test_hardware_field_resolution(flags, expected):
    defaults = {
        "is_mobile": False,
        "is_tablet": False,
        "is_pc": False,
        "is_bot": False,
    }
    defaults.update(flags)

    assert (
        ConnectionHardwareStatsMiddleware.resolve_field(mock.Mock(**defaults))
        == expected
    )


@pytest.mark.django_db
def test_request_without_user_agent_header_is_not_counted_by_method_stats():
    middleware = ConnectionMethodStatsMiddleware(lambda request: None)
    request = mock.Mock(path_info="/portfolio/", META={})

    middleware.record(request)

    assert ConnectionMethodStats.objects.count() == 0


@pytest.mark.django_db
def test_request_without_user_agent_object_is_not_counted_by_hardware_stats():
    middleware = ConnectionHardwareStatsMiddleware(lambda request: None)
    request = mock.Mock(path_info="/portfolio/", spec=["path_info"])

    middleware.record(request)

    assert ConnectionHardwareStats.objects.count() == 0


@pytest.mark.django_db
def test_unclassifiable_user_agent_is_not_counted():
    middleware = ConnectionHardwareStatsMiddleware(lambda request: None)
    request = mock.Mock(
        path_info="/portfolio/",
        user_agent=mock.Mock(
            is_mobile=False, is_tablet=False, is_pc=False, is_bot=False
        ),
    )

    middleware.record(request)

    assert ConnectionHardwareStats.objects.count() == 0


def test_hardware_field_resolution_returns_none_for_unknown_agent():
    unknown = mock.Mock(
        is_mobile=False, is_tablet=False, is_pc=False, is_bot=False
    )

    assert ConnectionHardwareStatsMiddleware.resolve_field(unknown) is None
