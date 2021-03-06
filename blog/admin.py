from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin    # 관리자페이지에서 카테고리를 트리형식으로
from blog.models.default import MainMenu, SiteInfo, WorldSocialAccount, LocalSocialAccount
from blog.models.boards import ProjectPost, OnlineStudyPost, BlogPost, InterestingOpenSourcePost, BooksPost, Tag, Like, Bookmark
from django_summernote.admin import SummernoteModelAdmin
# Register your models here.

class SiteInfoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SiteInfo._meta.get_fields()]
    list_display_links = ['id', 'phone_number','office_email']

class WorldSocialAccountAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WorldSocialAccount._meta.get_fields()]
    list_display_links = ['id']

class LocalSocialAccountAdmin(admin.ModelAdmin):
    list_display = [field.name for field in LocalSocialAccount._meta.get_fields()]
    list_display_links = ['id']


class InterestingOpenSourcePostAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


admin.site.register(MainMenu, DraggableMPTTAdmin)
admin.site.register(SiteInfo, SiteInfoAdmin)
admin.site.register(WorldSocialAccount, WorldSocialAccountAdmin)
admin.site.register(LocalSocialAccount, LocalSocialAccountAdmin)
admin.site.register(InterestingOpenSourcePost, InterestingOpenSourcePostAdmin)