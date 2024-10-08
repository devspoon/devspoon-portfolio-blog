import logging

from django.conf import settings
from rangefilter.filters import DateRangeFilter

from board.admin.common_admin import board_admin_site
from board.models.board import Visiter
from board.models.board_reply import VisiterReply
from common.mixin.admin.redis_cache_handler import (
    AdminCacheCleanPostMixin,
    AdminCacheCleanReplyMixin,
    AdminCommonActionMixin,
)
from common.mixin.admin.actions import CustomActionsAdminMixin
from common.mixin.admin.trim_html_tags import TrimHtmlTagsAdminMixin

logger = logging.getLogger(getattr(settings, "BOARD_LOGGER", "django"))


class VisiterBoardAdmin(CustomActionsAdminMixin, TrimHtmlTagsAdminMixin, AdminCommonActionMixin, AdminCacheCleanPostMixin):
    list_per_page = 20
    cache_prefix = "board:Visiter"
    cache_reply_prefix = "board:VisiterReply"

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
        "copy_selected_items",
    ]
    exclude = ("table_name",)

    def save_model(self, request, obj, form, change):
        obj.table_name = obj._meta.db_table
        super().save_model(request, obj, form, change)


class VisiterReplyAdmin(CustomActionsAdminMixin, TrimHtmlTagsAdminMixin, AdminCommonActionMixin, AdminCacheCleanReplyMixin):
    list_per_page = 20
    cache_prefix = "blog:VisiterReply"

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
        "copy_selected_items",
    ]


board_admin_site.register(Visiter, VisiterBoardAdmin)
board_admin_site.register(VisiterReply, VisiterReplyAdmin)
