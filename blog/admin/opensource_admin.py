from django.contrib import admin

from blog.models.boards import OpenSourcePost
from blog.models.reply import OpenSourcePostReply
from django_summernote.admin import SummernoteModelAdmin


class OpenSourcePostAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


@admin.register(OpenSourcePostReply)
class OpenSourcePostReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','post']
    list_display_links = ['id', 'author']


admin.site.register(OpenSourcePost, OpenSourcePostAdmin)