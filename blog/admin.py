from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin    # 관리자페이지에서 카테고리를 트리형식으로
from blog.models.default import MainMenu, SiteInfo, WorldSocialAccount, LocalSocialAccount
from blog.models.boards import ProjectPost, OnlineStudyPost, BlogPost, OpenSourcePost, BooksPost, Tag
from blog.models.reply import ProjectPostReply, OnlineStudyPostReply, BlogPostReply, OpenSourcePostReply, BooksPostReply
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


class ProjectPostAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


class OnlineStudyPostAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


class BlogPostAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


class OpenSourcePostAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


class BooksPostAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


@admin.register(ProjectPostReply)
class ProjectPostReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','post']
    list_display_links = ['id', 'author']


@admin.register(OnlineStudyPostReply)
class OnlineStudyPostReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','post']
    list_display_links = ['id', 'author']


@admin.register(BlogPostReply)
class BlogPostReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','post']
    list_display_links = ['id', 'author']


@admin.register(OpenSourcePostReply)
class OpenSourcePostReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','post']
    list_display_links = ['id', 'author']


@admin.register(BooksPostReply)
class BooksPostReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','post']
    list_display_links = ['id', 'author']


admin.site.register(MainMenu, DraggableMPTTAdmin)
admin.site.register(SiteInfo, SiteInfoAdmin)
admin.site.register(WorldSocialAccount, WorldSocialAccountAdmin)
admin.site.register(LocalSocialAccount, LocalSocialAccountAdmin)

admin.site.register(ProjectPost, ProjectPostAdmin)
admin.site.register(OnlineStudyPost, OnlineStudyPostAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(OpenSourcePost, OpenSourcePostAdmin)
admin.site.register(BooksPost, BooksPostAdmin)

