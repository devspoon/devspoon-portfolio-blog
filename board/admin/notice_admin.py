from django.contrib import admin
from board.models.board import Notice
from django_summernote.admin import SummernoteModelAdmin
from board.models.board_reply import NoticeReply

class NoticeBoardAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


@admin.register(NoticeReply)
class NoticeReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','board']
    list_display_links = ['id', 'author']


admin.site.register(Notice, NoticeBoardAdmin)