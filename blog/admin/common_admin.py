import logging

from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite

from blog.models.blog import Tag

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


class BlogAdminSite(AdminSite):
    site_header = "Blog Admin"
    site_title = "Blog Admin Portal"
    index_title = "Welcome to Blog Admin Portal"


blog_admin_site = BlogAdminSite(name="blog_admin")


class TagAdmin(admin.ModelAdmin):
    list_display = ("tag",)
    list_display_links = [
        "tag",
    ]


blog_admin_site.register(Tag, TagAdmin)
