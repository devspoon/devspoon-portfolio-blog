import json

from django.contrib import admin
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers

from ..models import ConnectionMethodStats, ConnectionHardwareStats


class ConnectionMethodStatsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ConnectionMethodStats._meta.get_fields()]

    change_list_template = (
        "admin/custom_middlewares/connection_method_stats/change_list.html"
    )

    def changelist_view(self, request, extra_context=None):
        # created_at__day은 '일(day of month)'만 비교해 다른 달의 row까지 섞였다.
        # 집계키인 stat_date로 오늘 row만 조회한다.
        stat_data = ConnectionMethodStats.objects.filter(
            stat_date=timezone.localdate()
        ).values("win", "mac", "iph", "android", "oth")

        # data = newstats.objects.all()
        # newdata = serializers.serialize('json', list(data), fields=("win","mac","iph","android","oth"))
        # print(newdata)

        as_json = json.dumps(list(stat_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"stat_data": as_json}

        return super().changelist_view(request, extra_context=extra_context)


class ConnectionHardwareStatsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ConnectionHardwareStats._meta.get_fields()]

    change_list_template = (
        "admin/custom_middlewares/connection_hardware_stats/change_list.html"
    )

    def changelist_view(self, request, extra_context=None):
        # created_at__day은 '일(day of month)'만 비교해 다른 달의 row까지 섞였다.
        # 집계키인 stat_date로 오늘 row만 조회한다.
        stat_data = ConnectionHardwareStats.objects.filter(
            stat_date=timezone.localdate()
        ).values("mobile", "tablet", "pc", "bot")

        # data = newstats.objects.all()
        # newdata = serializers.serialize('json', list(data), fields=("mobile","tablet","pc","bot"))
        # print(newdata)

        as_json = json.dumps(list(stat_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"stat_data": as_json}

        return super().changelist_view(request, extra_context=extra_context)
