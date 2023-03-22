import json 

from django.contrib import admin

from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from middlewares.

from home.admin.default_admin import home_admin_site
from ..models import newstats
import logging
from django.conf import settings
logger = logging.getLogger(getattr(settings, "COMMON_LOGGER", "django"))
@home_admin_site.register(newstats)
class NewStatsAdmin(admin.ModelAdmin):

    def changelist_view(self, request, extra_context=None):

        stat_data = (
            newstats.objects.annotate().values("win","mac","iph","android","oth")
        )

        # data = newstats.objects.all()
        # newdata = serializers.serialize('json', list(data), fields=("win","mac","iph","android","oth"))
        # print(newdata)

        as_json = json.dumps(list(stat_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"stat_data": as_json}

        return super().changelist_view(request, extra_context=extra_context)


