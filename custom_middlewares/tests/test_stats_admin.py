import json
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from custom_middlewares.models import (
    ConnectionHardwareStats,
    ConnectionMethodStats,
)
from users.models import User

pytestmark = [pytest.mark.middlewares, pytest.mark.django_db]


@pytest.fixture
def admin_client(client):
    User.objects.create_superuser(
        username="statsadmin",
        email="statsadmin@devspoon.com",
        password="password",
    )
    client.login(username="statsadmin", password="password")
    return client


def stat_data_of(response):
    return json.loads(response.context["stat_data"])


def test_method_stats_changelist_shows_today(admin_client):
    today = timezone.localdate()
    ConnectionMethodStats.objects.create(stat_date=today, win=4, mac=2)

    response = admin_client.get(
        reverse("home_admin:home_connectionmethodstats_changelist")
    )

    assert response.status_code == 200
    assert stat_data_of(response) == [
        {"win": 4, "mac": 2, "iph": 0, "android": 0, "oth": 0}
    ]


def test_method_stats_changelist_ignores_same_day_of_other_months(admin_client):
    """created_at__day은 '일'만 비교해 다른 달의 row까지 집계에 섞였다."""
    today = timezone.localdate()
    ConnectionMethodStats.objects.create(stat_date=today, win=4)
    # 같은 '일'이지만 다른 달
    ConnectionMethodStats.objects.create(
        stat_date=today - timedelta(days=28), win=999
    )

    response = admin_client.get(
        reverse("home_admin:home_connectionmethodstats_changelist")
    )

    stat_data = stat_data_of(response)
    assert len(stat_data) == 1
    assert stat_data[0]["win"] == 4


def test_hardware_stats_changelist_shows_today(admin_client):
    today = timezone.localdate()
    ConnectionHardwareStats.objects.create(stat_date=today, pc=7, mobile=3)

    response = admin_client.get(
        reverse("home_admin:home_connectionhardwarestats_changelist")
    )

    assert response.status_code == 200
    assert stat_data_of(response) == [
        {"mobile": 3, "tablet": 0, "pc": 7, "bot": 0}
    ]


def test_changelist_works_with_no_rows_for_today(admin_client):
    response = admin_client.get(
        reverse("home_admin:home_connectionmethodstats_changelist")
    )

    assert response.status_code == 200
    assert stat_data_of(response) == []


def test_changelist_renders_stat_date_column(admin_client):
    """list_display는 모델 필드에서 만들어지므로 stat_date가 포함되어야 한다."""
    ConnectionMethodStats.objects.create(stat_date=timezone.localdate(), win=1)

    response = admin_client.get(
        reverse("home_admin:home_connectionmethodstats_changelist")
    )

    assert b"stat_date" in response.content.lower().replace(b"-", b"_")
