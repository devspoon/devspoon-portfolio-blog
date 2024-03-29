# from .boards import ProjectPost, OnlineStudyPost, BlogPost, OpenSourcePost, BooksPost, Tag
import logging

from django.conf import settings
from django.db import models

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


class ProjectLike(models.Model):
    users = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE
    )
    projects = models.ForeignKey(
        "blog.ProjectPost", blank=True, null=True, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class OnlineStudyLike(models.Model):
    users = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE
    )
    online_study = models.ForeignKey(
        "blog.OnlineStudyPost", blank=True, null=True, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class BlogLike(models.Model):
    users = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE
    )
    blogs = models.ForeignKey(
        "blog.BlogPost", blank=True, null=True, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class OpenSourceLike(models.Model):
    users = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE
    )
    open_sources = models.ForeignKey(
        "blog.OpenSourcePost", blank=True, null=True, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class BooksLike(models.Model):
    users = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE
    )
    books = models.ForeignKey(
        "blog.BooksPost", blank=True, null=True, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
