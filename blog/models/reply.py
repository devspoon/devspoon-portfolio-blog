from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from django.urls import reverse

from django.db import models
from .boards import ProjectPost, OnlineStudyPost, BlogPost, OpenSourcePost, BooksPost

class Reply(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']
        app_label = "blog"

    def __str__(self):
        return self.content


class ProjectPostReply(Reply):
    post = models.ForeignKey(ProjectPost, on_delete=models.CASCADE)

    class Meta:
        db_table = 'project_post_reply'
        verbose_name = _('project post reply')
        verbose_name_plural = _('project post reply')


class OnlineStudyPostReply(Reply):
    post = models.ForeignKey(OnlineStudyPost, on_delete=models.CASCADE)

    class Meta:
        db_table = 'online_study_post_reply'
        verbose_name = _('online study post reply')
        verbose_name_plural = _('online study post reply')


class BlogPostReply(Reply):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)

    class Meta:
        db_table = 'blog_post_reply'
        verbose_name = _('blog post reply')
        verbose_name_plural = _('blog post reply') 


class OpenSourcePostReply(Reply):
    post = models.ForeignKey(OpenSourcePost, on_delete=models.CASCADE)

    class Meta:
        db_table = 'open_source_post_reply'
        verbose_name = _('open source post reply')
        verbose_name_plural = _('open source post reply')


class BooksPostReply(Reply):
    post = models.ForeignKey(BooksPost, on_delete=models.CASCADE)

    class Meta:
        db_table = 'books_post_reply'
        verbose_name = _('books post reply')
        verbose_name_plural = _('books post reply')
