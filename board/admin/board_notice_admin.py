from django.contrib import admin
from board.models.board import Notice
from django_summernote.admin import SummernoteModelAdmin
from board.models.board_reply import NoticeReply
from board.admin.board_common_admin import board_admin_site

class NoticeBoardAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


class NoticeReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','board']
    list_display_links = ['id', 'author']


board_admin_site.register(Notice, NoticeBoardAdmin)
board_admin_site.register(NoticeReply, NoticeReplyAdmin)