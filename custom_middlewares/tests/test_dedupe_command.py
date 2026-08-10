from datetime import date, datetime, timezone as dt_timezone
from io import StringIO

import pytest
from django.core.management import call_command

from custom_middlewares.models import (
    ConnectionHardwareStats,
    ConnectionMethodStats,
)

pytestmark = [pytest.mark.middlewares, pytest.mark.django_db]

DAY_ONE = date(2026, 8, 5)
DAY_TWO = date(2026, 8, 6)


def make_legacy_row(model, created_on: date, **counters):
    """stat_date가 없던 시절의 row를 재현한다."""
    row = model.objects.create(**counters)
    model.objects.filter(pk=row.pk).update(
        stat_date=None,
        created_at=datetime(
            created_on.year,
            created_on.month,
            created_on.day,
            12,
            0,
            tzinfo=dt_timezone.utc,
        ),
    )
    return row


def run_command(*args):
    out = StringIO()
    call_command("dedupe_connection_stats", *args, stdout=out)
    return out.getvalue()


def test_duplicates_are_merged_and_counts_are_summed():
    make_legacy_row(ConnectionMethodStats, DAY_ONE, win=3, oth=1)
    make_legacy_row(ConnectionMethodStats, DAY_ONE, win=4, mac=2)

    run_command()

    stats = ConnectionMethodStats.objects.get()
    assert stats.stat_date == DAY_ONE
    assert stats.win == 7
    assert stats.mac == 2
    assert stats.oth == 1


def test_different_dates_are_not_merged():
    make_legacy_row(ConnectionMethodStats, DAY_ONE, win=1)
    make_legacy_row(ConnectionMethodStats, DAY_ONE, win=2)
    make_legacy_row(ConnectionMethodStats, DAY_TWO, win=5)

    run_command()

    assert ConnectionMethodStats.objects.count() == 2
    assert ConnectionMethodStats.objects.get(stat_date=DAY_ONE).win == 3
    assert ConnectionMethodStats.objects.get(stat_date=DAY_TWO).win == 5


def test_stat_date_is_backfilled_for_single_rows():
    make_legacy_row(ConnectionHardwareStats, DAY_ONE, pc=9)

    run_command()

    stats = ConnectionHardwareStats.objects.get()
    assert stats.stat_date == DAY_ONE
    assert stats.pc == 9


def test_command_is_idempotent():
    make_legacy_row(ConnectionMethodStats, DAY_ONE, win=3)
    make_legacy_row(ConnectionMethodStats, DAY_ONE, win=4)

    run_command()
    run_command()

    assert ConnectionMethodStats.objects.count() == 1
    assert ConnectionMethodStats.objects.get().win == 7


def test_dry_run_changes_nothing():
    make_legacy_row(ConnectionMethodStats, DAY_ONE, win=3)
    make_legacy_row(ConnectionMethodStats, DAY_ONE, win=4)

    output = run_command("--dry-run")

    assert ConnectionMethodStats.objects.count() == 2
    assert ConnectionMethodStats.objects.filter(stat_date=None).count() == 2
    assert "dry-run" in output


def test_both_tables_are_processed():
    make_legacy_row(ConnectionMethodStats, DAY_ONE, win=1)
    make_legacy_row(ConnectionMethodStats, DAY_ONE, win=1)
    make_legacy_row(ConnectionHardwareStats, DAY_ONE, pc=1)
    make_legacy_row(ConnectionHardwareStats, DAY_ONE, pc=1)

    run_command()

    assert ConnectionMethodStats.objects.get().win == 2
    assert ConnectionHardwareStats.objects.get().pc == 2
