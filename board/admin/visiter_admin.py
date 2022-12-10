from django.contrib import admin
from board.models.board import Visiter
from django_summernote.admin import SummernoteModelAdmin
from board.models.board_reply import VisiterReply
from board.admin.common_admin import board_admin_site
from mixins.admin.admin_common_mixin import AdminCommonMixin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter

class VisiterBoardAdmin(SummernoteModelAdmin, AdminCommonMixin):
    list_per_page = 20

    list_display = ['id','author','title','is_deleted','is_hidden']
    list_display_links = ['id', 'author','title']
    list_filter = ("author", ('created_at', DateRangeFilter), 'is_deleted', 'is_hidden')
    list_editable = ('is_deleted','is_hidden')
    search_fields = ('author__username', 'title','content')
    summernote_fields = ('content',)
    actions = ["set_delete","set_activate","set_hidden","set_visible"]


class VisiterReplyAdmin(admin.ModelAdmin, AdminCommonMixin):
    list_per_page = 20

    list_display = ['id','author','board']
    list_display_links = ['id', 'author']
    list_filter = ("author", ('created_at', DateRangeFilter))
    search_fields = ('author__username', 'comment')
    actions = ["set_delete","set_activate","set_hidden","set_visible"]


board_admin_site.register(Visiter, VisiterBoardAdmin)
board_admin_site.register(VisiterReply, VisiterReplyAdmin)