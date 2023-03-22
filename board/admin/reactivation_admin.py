from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter

from board.admin.common_admin import board_admin_site
from board.models.board import Reactivation
from board.models.board_reply import ReactivationReply
from common.components.admin.admin_components import AdminCommonAction


class ReactivationBoardAdmin(SummernoteModelAdmin, AdminCommonAction):
    list_per_page = 20

    list_display = ["id", "author", "title", "is_deleted", "is_hidden"]
    list_display_links = ["id", "author", "title"]
    list_filter = ("author", ("created_at", DateRangeFilter), "is_deleted", "is_hidden")
    list_editable = ("is_deleted", "is_hidden")
    search_fields = ("author__username", "title", "content")
    summernote_fields = ("content",)
    actions = ["set_delete", "set_activate", "set_hidden", "set_visible"]


class ReactivationReplyAdmin(admin.ModelAdmin, AdminCommonAction):
    list_per_page = 20

    list_display = ["id", "author", "board"]
    list_display_links = ["id", "author"]
    list_filter = ("author", ("created_at", DateRangeFilter))
    search_fields = ("author__username", "comment")
    actions = ["set_delete", "set_activate", "set_hidden", "set_visible"]


board_admin_site.register(Reactivation, ReactivationBoardAdmin)
board_admin_site.register(ReactivationReply, ReactivationReplyAdmin)
