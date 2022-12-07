from django.contrib import admin
from board.models.board import Reactivation
from django_summernote.admin import SummernoteModelAdmin
from board.models.board_reply import ReactivationReply
from board.admin.board_common_admin import board_admin_site

class ReactivationBoardAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


class ReactivationReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','board']
    list_display_links = ['id', 'author']


board_admin_site.register(Reactivation, ReactivationBoardAdmin)
board_admin_site.register(ReactivationReply, ReactivationReplyAdmin)