from django.contrib import admin
from board.models.board import Visiter
from django_summernote.admin import SummernoteModelAdmin
from board.models.board_reply import VisiterReply

class VisiterBoardAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


@admin.register(VisiterReply)
class VisiterReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','board']
    list_display_links = ['id', 'author']


admin.site.register(Visiter, VisiterBoardAdmin)