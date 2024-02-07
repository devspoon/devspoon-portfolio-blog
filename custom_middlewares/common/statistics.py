import logging

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from ..models import ConnectionHardwareStats, ConnectionMethodStats

logger = logging.getLogger(getattr(settings, "COMMON_LOGGER", "django"))


class ConnectionMethodStatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def stats(self, os_info):
        with transaction.atomic():
            count = ConnectionMethodStats.objects.filter(
                created_at__day=timezone.now().date().day
            )
            if not count:
                ConnectionMethodStats.objects.create(created_at=timezone.now())

            if "Windows" in os_info:
                count.update(win=F("win") + 1)
            elif "mac" in os_info:
                count.update(mac=F("mac") + 1)
            elif "iPhone" in os_info:
                count.update(iph=F("iph") + 1)
            elif "Android" in os_info:
                count.update(android=F("android") + 1)
            else:
                count.update(oth=F("oth") + 1)

    def __call__(self, request):
        if "HTTP_USER_AGENT" in request.META:
            if "admin" not in request.path:
                self.stats(request.META["HTTP_USER_AGENT"])

        response = self.get_response(request)

        return response


class ConnectionHardwareStatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "admin" not in request.path:
            with transaction.atomic():
                count = ConnectionHardwareStats.objects.filter(
                    created_at__day=timezone.now().date().day
                )
                if not count:
                    ConnectionHardwareStats.objects.create(created_at=timezone.now())

                if request.user_agent.is_mobile:
                    count.update(mobile=F("mobile") + 1)
                elif request.user_agent.is_tablet:
                    count.update(tablet=F("tablet") + 1)
                elif request.user_agent.is_pc:
                    count.update(pc=F("pc") + 1)
                elif request.user_agent.is_bot:
                    count.update(bot=F("bot") + 1)

        response = self.get_response(request)

        return response
