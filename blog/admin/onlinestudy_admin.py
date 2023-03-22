import logging

from django.conf import settings
from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter

from blog.admin.common_admin import blog_admin_site
from blog.models.blog import OnlineStudyPost
from blog.models.blog_reply import OnlineStudyPostReply
from common.components.admin.admin_components import AdminCommonAction

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


class OnlineStudyPostAdmin(SummernoteModelAdmin, AdminCommonAction):
    list_per_page = 20

    list_display = ["id", "author", "title", "is_deleted", "is_hidden"]
    list_display_links = ["id", "author", "title"]
    list_filter = ("author", ("created_at", DateRangeFilter), "is_deleted", "is_hidden")
    list_editable = ("is_deleted", "is_hidden")
    search_fields = ("author__username", "title", "content")
    summernote_fields = ("content",)
    actions = ["set_delete", "set_activate", "set_hidden", "set_visible"]
    filter_horizontal = ("tag_set",)
    date_hierarchy = "created_at"


class OnlineStudyPostReplyAdmin(admin.ModelAdmin, AdminCommonAction):
    list_per_page = 20

    list_display = ["id", "author", "post"]
    list_display_links = ["id", "author"]
    list_filter = ("author", ("created_at", DateRangeFilter))
    search_fields = ("author__username", "comment")
    actions = ["set_delete", "set_activate", "set_hidden", "set_visible"]


blog_admin_site.register(OnlineStudyPost, OnlineStudyPostAdmin)
blog_admin_site.register(OnlineStudyPostReply, OnlineStudyPostReplyAdmin)
