import logging

from django.conf import settings
from rangefilter.filters import DateRangeFilter

from board.admin.common_admin import board_admin_site
from board.models.board import Notice
from board.models.board_reply import NoticeReply
from common.components.admin.admin_components import (
    AdminCacheCleanPost,
    AdminCacheCleanReply,
    AdminCommonAction,
)

logger = logging.getLogger(getattr(settings, "BOARD_LOGGER", "django"))


class NoticeBoardAdmin(AdminCommonAction, AdminCacheCleanPost):
    list_per_page = 20
    cache_prefix = "board:Notice"
    cache_reply_prefix = "board:NoticeReply"

    list_display = ["id", "author", "title", "is_deleted", "is_hidden"]
    list_display_links = ["id", "author", "title"]
    list_filter = ("author", ("created_at", DateRangeFilter), "is_deleted", "is_hidden")
    list_editable = ("is_deleted", "is_hidden")
    search_fields = ("author__username", "title", "content")
    summernote_fields = ("content",)
    actions = [
        "set_delete",
        "set_activate",
        "set_hidden",
        "set_visible",
        "delete_all_cache",
        "delete_selected_items",
    ]

    def get_actions(self, request):
        actions = super(NoticeBoardAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions


class NoticeReplyAdmin(AdminCommonAction, AdminCacheCleanReply):
    list_per_page = 20
    cache_prefix = "blog:NoticeReply"

    list_display = ["id", "author", "board"]
    list_display_links = ["id", "author"]
    list_filter = ("author", ("created_at", DateRangeFilter))
    search_fields = ("author__username", "comment")
    actions = [
        "set_delete",
        "set_activate",
        "set_hidden",
        "set_visible",
        "delete_all_cache",
        "delete_selected_items",
    ]

    def get_actions(self, request):
        actions = super(NoticeReplyAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions


board_admin_site.register(Notice, NoticeBoardAdmin)
board_admin_site.register(NoticeReply, NoticeReplyAdmin)
