from django.contrib import admin

from blog.models.blog import OpenSourcePost
from blog.models.blog_reply import OpenSourcePostReply
from django_summernote.admin import SummernoteModelAdmin
from blog.admin.blog_common_admin import blog_admin_site


class OpenSourcePostAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


class OpenSourcePostReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','post']
    list_display_links = ['id', 'author']


blog_admin_site.register(OpenSourcePost, OpenSourcePostAdmin)
blog_admin_site.register(OpenSourcePostReply, OpenSourcePostReplyAdmin)