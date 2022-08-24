from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from django.urls import reverse

from django.db import models
#from .boards import ProjectPost, OnlineStudyPost, BlogPost, OpenSourcePost, BooksPost

class Reply(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField(default='', blank=False, verbose_name=_('Comment'))
    depth = models.SmallIntegerField(default=0, verbose_name=_('Reply depth'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='parent_set' , null=True, blank=True, default = None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.comment


class ProjectPostReply(Reply):
    post = models.ForeignKey('blog.ProjectPost', on_delete=models.CASCADE)

    class Meta:
        db_table = 'project_post_reply'
        verbose_name = _('project post reply')
        verbose_name_plural = _('project post reply')


class OnlineStudyPostReply(Reply):
    post = models.ForeignKey('blog.OnlineStudyPost', on_delete=models.CASCADE)

    class Meta:
        db_table = 'online_study_post_reply'
        verbose_name = _('online study post reply')
        verbose_name_plural = _('online study post reply')


class BlogPostReply(Reply):
    post = models.ForeignKey('blog.BlogPost', on_delete=models.CASCADE)

    class Meta:
        db_table = 'blog_post_reply'
        verbose_name = _('blog post reply')
        verbose_name_plural = _('blog post reply')


class OpenSourcePostReply(Reply):
    post = models.ForeignKey('blog.OpenSourcePost', on_delete=models.CASCADE)

    class Meta:
        db_table = 'open_source_post_reply'
        verbose_name = _('open source post reply')
        verbose_name_plural = _('open source post reply')


class BooksPostReply(Reply):
    post = models.ForeignKey('blog.BooksPost', on_delete=models.CASCADE)

    class Meta:
        db_table = 'books_post_reply'
        verbose_name = _('books post reply')
        verbose_name_plural = _('books post reply')
