import logging

from django.conf import settings
from django.db import models
from django.db.models import F
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

# from .blog import BlogPost, BooksPost, OnlineStudyPost, OpenSourcePost, ProjectPost

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


class BlogReplyMixin(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField(default="", blank=False, verbose_name=_("Comment"))
    depth = models.SmallIntegerField(default=0, verbose_name=_("Reply depth"))
    group = models.SmallIntegerField(default=0, verbose_name=_("Reply group"))
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="parent_set",
        null=True,
        blank=True,
        default=None,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.comment


class ProjectPostReply(BlogReplyMixin):
    post = models.ForeignKey("blog.ProjectPost", on_delete=models.CASCADE)

    class Meta:
        db_table = "project_post_reply"
        verbose_name = _("project post reply")
        verbose_name_plural = _("project post reply")
        ordering = [
            ("group"),
        ]


class OnlineStudyPostReply(BlogReplyMixin):
    post = models.ForeignKey("blog.OnlineStudyPost", on_delete=models.CASCADE)

    class Meta:
        db_table = "online_study_post_reply"
        verbose_name = _("online study post reply")
        verbose_name_plural = _("online study post reply")
        ordering = [
            ("group"),
        ]


class BlogPostReply(BlogReplyMixin):
    post = models.ForeignKey("blog.BlogPost", on_delete=models.CASCADE)

    class Meta:
        db_table = "blog_post_reply"
        verbose_name = _("blog post reply")
        verbose_name_plural = _("blog post reply")
        ordering = [
            ("group"),
        ]


class OpenSourcePostReply(BlogReplyMixin):
    post = models.ForeignKey("blog.OpenSourcePost", on_delete=models.CASCADE)

    class Meta:
        db_table = "open_source_post_reply"
        verbose_name = _("open source post reply")
        verbose_name_plural = _("open source post reply")
        ordering = [
            ("group"),
        ]


class BooksPostReply(BlogReplyMixin):
    post = models.ForeignKey("blog.BooksPost", on_delete=models.CASCADE)

    class Meta:
        db_table = "books_post_reply"
        verbose_name = _("books post reply")
        verbose_name_plural = _("books post reply")
        ordering = [
            ("group"),
        ]


@receiver(post_delete)
def auto_delete_file_on_delete_for_blog(sender, instance=None, **kwargs):
    list_of_models = (
        "ProjectPostReply",
        "OnlineStudyPostReply",
        "BlogPostReply",
        "OpenSourcePostReply",
        "BooksPostReply",
    )
    if sender.__name__ in list_of_models:  # this is the dynamic part you want
        # post_delete 시점에는 행이 이미 지워져 있어 다시 조회하면 DoesNotExist로
        # 삭제 전체가 롤백된다. 조건부 UPDATE 한 문장으로 줄이고 0 아래로 내려가지 않게 한다.
        post_model = sender._meta.get_field("post").related_model
        post_model.objects.filter(pk=instance.post_id, reply_count__gt=0).update(
            reply_count=F("reply_count") - 1
        )
