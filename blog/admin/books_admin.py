import logging

from django.conf import settings
from rangefilter.filters import DateRangeFilter

from blog.admin.common_admin import blog_admin_site
from blog.models.blog import BooksPost
from blog.models.blog_reply import BooksPostReply
from common.components.admin.admin_components import (
    AdminCacheCleanPost,
    AdminCacheCleanReply,
    AdminCommonAction,
)

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


class BooksPostAdmin(AdminCommonAction, AdminCacheCleanPost):
    list_per_page = 20
    cache_prefix = "blog:Books"
    cache_reply_prefix = "blog:BooksReply"

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
    filter_horizontal = ("tag_set",)
    date_hierarchy = "created_at"
    exclude = ("table_name",)

    def get_actions(self, request):
        actions = super(BooksPostAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions

    def save_model(self, request, obj, form, change):
        obj.table_name = obj._meta.db_table
        super().save_model(request, obj, form, change)


class BooksPostReplyAdmin(AdminCommonAction, AdminCacheCleanReply):
    list_per_page = 20
    cache_prefix = "blog:BooksReply"

    list_display = ["id", "author", "post"]
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
        actions = super(BooksPostReplyAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions


blog_admin_site.register(BooksPost, BooksPostAdmin)
blog_admin_site.register(BooksPostReply, BooksPostReplyAdmin)
