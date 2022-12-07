from django.contrib import admin
from blog.models.blog import OnlineStudyPost
from django_summernote.admin import SummernoteModelAdmin
from blog.models.blog_reply import OnlineStudyPostReply
from blog.admin.blog_common_admin import blog_admin_site


class OnlineStudyPostAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


class OnlineStudyPostReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','post']
    list_display_links = ['id', 'author']


blog_admin_site.register(OnlineStudyPost, OnlineStudyPostAdmin)
blog_admin_site.register(OnlineStudyPostReply, OnlineStudyPostReplyAdmin)