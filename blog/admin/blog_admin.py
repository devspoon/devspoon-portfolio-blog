import logging

from django.conf import settings
from rangefilter.filters import DateRangeFilter

from blog.admin.common_admin import blog_admin_site
from blog.models.blog import BlogPost
from blog.models.blog_reply import BlogPostReply
from common.mixin.admin.redis_cache_handler import (
    AdminCacheCleanPostMixin,
    AdminCacheCleanReplyMixin,
    AdminCommonActionMixin,
)
from common.mixin.admin.actions import CustomActionsAdminMixin
from common.mixin.admin.trim_html_tags import TrimHtmlTagsAdminMixin

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


class BlogPostAdmin(CustomActionsAdminMixin, TrimHtmlTagsAdminMixin, AdminCommonActionMixin, AdminCacheCleanPostMixin):
    list_per_page = 20
    cache_prefix = "blog:Blog"
    cache_reply_prefix = "blog:BlogReply"

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
    filter_horizontal = ("tag_set",)
    date_hierarchy = "created_at"
    exclude = ("table_name",)
    # prepopulated_fields = {'slug' : ['title']}

    def save_model(self, request, obj, form, change):
        obj.table_name = obj._meta.db_table
        super().save_model(request, obj, form, change)


class BlogPostReplyAdmin(CustomActionsAdminMixin, TrimHtmlTagsAdminMixin, AdminCommonActionMixin, AdminCacheCleanReplyMixin):
    list_per_page = 20
    cache_prefix = "blog:BlogReply"

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
        "copy_selected_items",
    ]


blog_admin_site.register(BlogPost, BlogPostAdmin)
blog_admin_site.register(BlogPostReply, BlogPostReplyAdmin)
