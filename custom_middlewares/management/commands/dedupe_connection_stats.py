from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from custom_middlewares.models import ConnectionHardwareStats, ConnectionMethodStats

TARGET_MODELS = (ConnectionMethodStats, ConnectionHardwareStats)


class Command(BaseCommand):
    help = (
        "일별 접속 통계 테이블의 중복 row를 날짜별로 합산해 1개로 정리하고 "
        "stat_date를 backfill한다. 여러 번 실행해도 결과가 같다."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="변경 없이 정리 대상만 출력한다.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("dry-run: 변경하지 않는다."))

        for model in TARGET_MODELS:
            self.process_model(model, dry_run)

    def process_model(self, model, dry_run):
        label = model._meta.db_table
        groups = defaultdict(list)
        for row in model.objects.all().order_by("pk"):
            groups[self.resolve_stat_date(row)].append(row)

        merged_dates = 0
        removed_rows = 0
        backfilled = 0

        for stat_date, rows in sorted(groups.items()):
            keeper = rows[0]
            duplicates = rows[1:]
            needs_backfill = keeper.stat_date != stat_date

            if not duplicates and not needs_backfill:
                continue

            totals = {
                field: sum(getattr(row, field) for row in rows)
                for field in model.COUNTER_FIELDS
            }

            if duplicates:
                merged_dates += 1
                removed_rows += len(duplicates)
            if needs_backfill:
                backfilled += 1

            self.stdout.write(
                f"{label} {stat_date}: rows={len(rows)} -> 1, {totals}"
            )

            if dry_run:
                continue

            with transaction.atomic():
                # 유니크 제약 충돌을 피하려고 중복 row를 먼저 지운다.
                if duplicates:
                    model.objects.filter(
                        pk__in=[row.pk for row in duplicates]
                    ).delete()

                keeper.stat_date = stat_date
                for field, value in totals.items():
                    setattr(keeper, field, value)
                keeper.save(update_fields=["stat_date", *model.COUNTER_FIELDS])

        summary = (
            f"{label}: 합산한 날짜 {merged_dates}건, 삭제한 중복 row {removed_rows}건, "
            f"stat_date backfill {backfilled}건"
        )
        self.stdout.write(self.style.SUCCESS(summary))

    @staticmethod
    def resolve_stat_date(row):
        """집계 기준 일자. stat_date가 비어 있으면 created_at에서 유도한다."""
        if row.stat_date:
            return row.stat_date
        return timezone.localtime(row.created_at).date()
