from django.contrib import admin
from board.models.board import Reactivation
from django_summernote.admin import SummernoteModelAdmin
from board.models.board_reply import ReactivationReply

class ReactivationBoardAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


@admin.register(ReactivationReply)
class ReactivationReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','board']
    list_display_links = ['id', 'author']


admin.site.register(Reactivation, ReactivationBoardAdmin)