from django.contrib import admin
from board.models.board import Visiter
from django_summernote.admin import SummernoteModelAdmin
from board.models.board_reply import VisiterReply
from board.admin.board_common_admin import board_admin_site

class VisiterBoardAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


class VisiterReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','board']
    list_display_links = ['id', 'author']


board_admin_site.register(Visiter, VisiterBoardAdmin)
board_admin_site.register(VisiterReply, VisiterReplyAdmin)