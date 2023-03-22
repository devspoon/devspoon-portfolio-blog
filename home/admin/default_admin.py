import logging

from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite
from mptt.admin import DraggableMPTTAdmin  # 관리자페이지에서 카테고리를 트리형식으로

from common.components.admin.admin_components import AdminCacheClean
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


class MainMenuAdmin(AdminCacheClean, DraggableMPTTAdmin):
    view_key = [
        "home:main_menu",
    ]
    template_key = [
        "home:template_main_menu_pc",
        "home:template_main_menu_mobile",
    ]

    actions = [
        "delete_all_cache",
        "delete_selected_items",
    ]

    def get_actions(self, request):
        actions = super(MainMenuAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions


class SiteInfoAdmin(AdminCacheClean, admin.ModelAdmin):
    list_display = [field.name for field in SiteInfo._meta.get_fields()]
    list_display_links = ["id", "phone_number", "office_email"]

    view_key = [
        "home:site_info",
    ]
    template_key = ""

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
