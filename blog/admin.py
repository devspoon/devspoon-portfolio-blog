from django.contrib import admin
from blog.models.siteinfo import MainMenu, SiteInfo, WorldSocialAccount, LocalSocialAccount
# Register your models here.

class MainMenuAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MainMenu._meta.get_fields()]
    list_display_links = ['id', 'menu_code', 'menu_name']

class SiteInfoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SiteInfo._meta.get_fields()]
    list_display_links = ['id', 'phone_number','email']

class WorldSocialAccountAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WorldSocialAccount._meta.get_fields()]
    list_display_links = ['id']

class LocalSocialAccountAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LocalSocialAccount._meta.get_fields()]
    list_display_links = ['id']

admin.site.register(MainMenu, MainMenuAdmin)
admin.site.register(SiteInfo, SiteInfoAdmin)
admin.site.register(WorldSocialAccount, WorldSocialAccountAdmin)
admin.site.register(LocalSocialAccount, LocalSocialAccountAdmin)