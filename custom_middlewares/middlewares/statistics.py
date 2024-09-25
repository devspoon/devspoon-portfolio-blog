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
        today = timezone.now().date()
        with transaction.atomic():
            # 오늘 날짜의 통계 가져오기 (잠금)
            (
                stats,
                created,
            ) = ConnectionMethodStats.objects.select_for_update().get_or_create(
                created_at__date=today
            )

            # 운영체제에 따라 카운트 업데이트
            if "Windows" in os_info:
                stats.win = F("win") + 1
            elif "mac" in os_info:
                stats.mac = F("mac") + 1
            elif "iPhone" in os_info:
                stats.iph = F("iph") + 1
            elif "Android" in os_info:
                stats.android = F("android") + 1
            else:
                stats.oth = F("oth") + 1

            stats.save()  # 변경 사항 저장

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
                today = timezone.now().date()
                # 오늘 날짜의 통계 가져오기
                (
                    stats,
                    created,
                ) = ConnectionHardwareStats.objects.select_for_update().get_or_create(
                    created_at__date=today
                )
                # 사용자 에이전트에 따라 카운트 업데이트
                if request.user_agent.is_mobile:
                    stats.mobile = F("mobile") + 1
                elif request.user_agent.is_tablet:
                    stats.tablet = F("tablet") + 1
                elif request.user_agent.is_pc:
                    stats.pc = F("pc") + 1
                elif request.user_agent.is_bot:
                    stats.bot = F("bot") + 1

                stats.save()  # 변경 사항 저장

        response = self.get_response(request)

        return response
