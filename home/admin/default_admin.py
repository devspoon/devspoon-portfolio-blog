from django.contrib import admin
from django.contrib.admin import AdminSite
from mptt.admin import DraggableMPTTAdmin    # 관리자페이지에서 카테고리를 트리형식으로
from home.models.default import MainMenu, SiteInfo

from custom_middlewares.models import ConnectionMethodStats
from custom_middlewares.admin.home_statistics_admin import ConnectionMethodStatsAdmin


class HomeAdminSite(AdminSite):
    site_header = "Home Admin"
    site_title = "Home Admin Portal"
    index_title = "Welcome to Home Admin Portal"

home_admin_site = HomeAdminSite(name='home_admin')


class SiteInfoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SiteInfo._meta.get_fields()]
    list_display_links = ['id', 'phone_number','office_email']


home_admin_site.register(MainMenu, DraggableMPTTAdmin)
home_admin_site.register(SiteInfo, SiteInfoAdmin)
home_admin_site.register(ConnectionMethodStats, ConnectionMethodStatsAdmin)