import logging

from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite
from mptt.admin import DraggableMPTTAdmin  # 관리자페이지에서 카테고리를 트리형식으로

from common.components.admin.admin_components import AdminCacheCleanFixedKey
from custom_middlewares.admin.home_statistics_admin import (
    ConnectionHardwareStatsAdmin,
    ConnectionMethodStatsAdmin,
)
from custom_middlewares.models import ConnectionHardwareStats, ConnectionMethodStats
from home.models.default import MainMenu, SiteInfo

logger = logging.getLogger(getattr(settings, "HOME_LOGGER", "django"))


class HomeAdminSite(AdminSite):
    site_header = "Home Admin"
    site_title = "Home Admin Portal"
    index_title = "Welcome to Home Admin Portal"


home_admin_site = HomeAdminSite(name="home_admin")


class MainMenuAdmin(AdminCacheCleanFixedKey, DraggableMPTTAdmin):
    view_keys = [
        "home:main_menu:0:main_menu",
    ]

    actions = [
        "delete_all_cache",
        "delete_selected_items",
    ]

    def get_actions(self, request):
        actions = super(MainMenuAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions


class SiteInfoAdmin(AdminCacheCleanFixedKey, admin.ModelAdmin):
    list_display = [field.name for field in SiteInfo._meta.get_fields()]
    list_display_links = ["id", "phone_number", "office_email"]

    view_keys = [
        "home:site_info:0:site_info",
    ]

    actions = [
        "delete_all_cache",
        "delete_selected_items",
    ]

    def get_actions(self, request):
        actions = super(SiteInfoAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions


home_admin_site.register(MainMenu, MainMenuAdmin)
home_admin_site.register(SiteInfo, SiteInfoAdmin)
home_admin_site.register(ConnectionMethodStats, ConnectionMethodStatsAdmin)
home_admin_site.register(ConnectionHardwareStats, ConnectionHardwareStatsAdmin)
