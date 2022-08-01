import os
import logging

from django.utils.translation import gettext_lazy as _
from django.conf import settings
import re
from bs4 import BeautifulSoup as Bs

from django.urls import reverse

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete

from django.db import models
from django.db.models.constraints import UniqueConstraint
from utils.os.file_path_name_gen import date_upload_to_for_file


logger = logging.getLogger(__name__)

class Post(models.Model):
    # class Category(models.TextChoices):
    #     PROJECT = '0', _('Project')
    #     ONLINE_STUDY = '1', _('Online Study')
    #     BLOG = '2', _('Blog')
    #     INTERESTING_OPEN_SOURCE = '3', _('Interesting Open Source')
    #     BOOKS = '4', _('Books')

    class Difficulty(models.TextChoices):
        BEGINNER = '0', _('Beginner')
        INTERMEDIATE = '1', _('Intermediate')
        ADVANCED = '2', _('Advanced')

    class ProjectRole(models.TextChoices):
        OWNER = '0', _('Owner')
        MAINTAINER = '1', _('Maintainer')
        DEVELOPER = '2', _('Developer')
        REPORTER = '3', _('Reporter')
        GUEST = '4', _('Guest')

    class Branch(models.TextChoices):
        FRONTEND = '0', _('Frontend')
        BACKEND = '1', _('Backend')
        INFRASTRUCTURE = '2', _('Infrastructure')
        DATABASE = '3', _('Database')
        ANALYSIS = '4', _('Analysis')
        MONITORING = '5', _('Monitoring')

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Author'))
    title = models.CharField(max_length=200, blank=False, verbose_name=_('Title'))
    # category = models.CharField(max_length=15, choices = Category.choices, default=Category.BLOG, verbose_name=_('Category'))
    content = models.TextField(blank=False, verbose_name=_('Content'))
    title_image = models.ImageField(blank=True, verbose_name=_('title_image'))
    link1 = models.URLField(blank=True, verbose_name=_('Link1'))
    link2 = models.URLField(blank=True, verbose_name=_('Link2'))
    file1 = models.FileField(upload_to=date_upload_to_for_file, blank=True, verbose_name=_('file1'))
    file2 = models.FileField(upload_to=date_upload_to_for_file, blank=True, verbose_name=_('file2'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tag_set = models.ManyToManyField('Tag', blank=True, verbose_name=_('Tags Set'))

    like_count = models.IntegerField(default=0, verbose_name=_('Like Count'))
    bookmark_count = models.IntegerField(default=0, verbose_name=_('Bookmark Count'))


    class Meta:
        abstract = True
        #app_label = "blog"

    def tag_save(self):
        tags = re.findall(r'#(\w+)\b', self.content)

        if not tags:
            return

        for t in tags:
            tag, tag_created = Tag.objects.get_or_create(tag=t)
            self.tag_set.add(tag)

    @property
    def get_like_count(self):
        return self.like_user_set.count()

    @property
    def get_bookmark_count(self):
        return self.bookmark_user_set.count()

    def __str__(self):
        return self.title


class ProjectPost(Post):

    role = models.CharField(max_length=15, choices = Post.ProjectRole.choices, default=Post.ProjectRole.OWNER, verbose_name=_('Project Role'))
    dev_lang = models.CharField(max_length=20, blank=False, verbose_name=_('Development Language'))
    version = models.CharField(max_length=10, blank=False, verbose_name=_('Version'))
    branch = models.CharField(max_length=15, choices = Post.Branch.choices, default=Post.Branch.BACKEND, verbose_name=_('Project Branch'))
    repository = models.URLField(blank=True, verbose_name=_('Repository'))
    like_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
									   blank=True,
									   related_name='ProjectPost_like_set',
									   through='Like',verbose_name=_('Like Set'))

    bookmark_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
									   blank=True,
									   related_name='ProjectPost_bookmark_set',
									   through='Bookmark', verbose_name=_('Bookmark Set'))

    class Meta:
        db_table = 'project_post'
        verbose_name = _('project')
        verbose_name_plural = _('project')
        ordering = ['-created_at']


class OnlineStudyPost(Post):
    dev_lang = models.CharField(max_length=20, blank=False, verbose_name=_('Development Language'))
    branch = models.CharField(max_length=15, choices = Post.Branch.choices, default=Post.Branch.BACKEND, verbose_name=_('Project Branch'))
    difficulty_level = models.CharField(max_length=15, choices = Post.Difficulty.choices, default=Post.Difficulty.BEGINNER, verbose_name=_('Difficulty Level'))
    like_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
									   blank=True,
									   related_name='OnlineStudyPost_like_set',
									   through='Like',verbose_name=_('Like Set'))

    bookmark_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
									   blank=True,
									   related_name='OnlineStudyPost_bookmark_set',
									   through='Bookmark', verbose_name=_('Bookmark Set'))

    class Meta:
        db_table = 'online_study_post'
        verbose_name = _('online study')
        verbose_name_plural = _('online study')
        ordering = ['-created_at']


class BlogPost(Post):
    like_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
									   blank=True,
									   related_name='BlogPost_like_set',
									   through='Like',verbose_name=_('Like Set'))

    bookmark_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
									   blank=True,
									   related_name='BlogPost_bookmark_set',
									   through='Bookmark', verbose_name=_('Bookmark Set'))

    class Meta:
        db_table = 'blog_post'
        verbose_name = _('blog post')
        verbose_name_plural = _('blog post')
        ordering = ['-created_at']


class InterestingOpenSourcePost(Post):

    role = models.CharField(max_length=15, choices = Post.ProjectRole.choices, default=Post.ProjectRole.OWNER, verbose_name=_('Project Role'))
    dev_lang = models.CharField(max_length=20, blank=False, verbose_name=_('Development Language'))
    branch = models.CharField(max_length=15, choices = Post.Branch.choices, default=Post.Branch.BACKEND, verbose_name=_('Project Branch'))
    repository = models.URLField(blank=True, verbose_name=_('Repository'))
    difficulty_level = models.CharField(max_length=15, choices = Post.Difficulty.choices, default=Post.Difficulty.BEGINNER, verbose_name=_('Difficulty Level'))
    like_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
									   blank=True,
									   related_name='InterestingOpenSourcePost_like_set',
									   through='Like',verbose_name=_('Like Set'))

    bookmark_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
									   blank=True,
									   related_name='InterestingOpenSourcePost_bookmark_set',
									   through='Bookmark', verbose_name=_('Bookmark Set'))

    class Meta:
        db_table = 'interesting_open_source_post'
        verbose_name = _('interesting open source post')
        verbose_name_plural = _('interesting open source post')
        ordering = ['-created_at']


class BooksPost(Post):

    dev_lang = models.CharField(max_length=20, blank=False, verbose_name=_('Development Language'))
    branch = models.CharField(max_length=15, choices = Post.Branch.choices, default=Post.Branch.BACKEND, verbose_name=_('Project Branch'))
    difficulty_level = models.CharField(max_length=15, choices = Post.Difficulty.choices, default=Post.Difficulty.BEGINNER, verbose_name=_('Difficulty Level'))
    like_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
									   blank=True,
									   related_name='BooksPost_like_set',
									   through='Like',verbose_name=_('Like Set'))

    bookmark_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
									   blank=True,
									   related_name='BooksPost_bookmark_set',
									   through='Bookmark', verbose_name=_('Bookmark Set'))

    class Meta:
        db_table = 'books_post'
        verbose_name = _('books post')
        verbose_name_plural = _('books post')
        ordering = ['-created_at']


class Tag(models.Model):
    tag = models.CharField(max_length=140, unique=True)

    def __str__(self):
        return self.tag


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(ProjectPost, blank=True, null=True, on_delete=models.CASCADE)
    online_study = models.ForeignKey(OnlineStudyPost, blank=True, null=True, on_delete=models.CASCADE)
    blog = models.ForeignKey(BlogPost, blank=True, null=True, on_delete=models.CASCADE)
    interesting_open_source = models.ForeignKey(InterestingOpenSourcePost, blank=True, null=True, on_delete=models.CASCADE)
    books = models.ForeignKey(BooksPost, blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'project'], name='like unique with project'),
            UniqueConstraint(fields=['user', 'online_study'], name='like unique with online_study'),
            UniqueConstraint(fields=['user', 'blog'], name='like unique with blog'),
            UniqueConstraint(fields=['user', 'interesting_open_source'], name='like unique with interesting_open_source'),
            UniqueConstraint(fields=['user', 'books'], name='like unique with books'),
        ]
        ordering = ['-created_at']


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(ProjectPost, blank=True, null=True, on_delete=models.CASCADE)
    online_study = models.ForeignKey(OnlineStudyPost, blank=True, null=True, on_delete=models.CASCADE)
    blog = models.ForeignKey(BlogPost, blank=True, null=True, on_delete=models.CASCADE)
    interesting_open_source = models.ForeignKey(InterestingOpenSourcePost, blank=True, null=True, on_delete=models.CASCADE)
    books = models.ForeignKey(BooksPost, blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'project'], name='Bookmark unique with project'),
            UniqueConstraint(fields=['user', 'online_study'], name='Bookmark unique with online_study'),
            UniqueConstraint(fields=['user', 'blog'], name='Bookmark unique with blog'),
            UniqueConstraint(fields=['user', 'interesting_open_source'], name='Bookmark unique with interesting_open_source'),
            UniqueConstraint(fields=['user', 'books'], name='Bookmark unique with books'),
        ]
        ordering = ['-created_at']


def get_title_image_url_in_textfield(instance):
    for field in instance._meta.fields:
        field_name = field.name

        if field_name == 'content' :
            new_content = getattr(instance, field_name)
            html = Bs(new_content, 'html.parser')
            img_urls = [url['src'] for url in html.find_all('img')]

            if img_urls :
                setattr(instance, 'title_image',img_urls[0])
            else :
                setattr(instance, 'title_image','')


def auto_delete_file_on_save_for_blog(sender, instance):
    if not instance.pk:
        return False

    try:
        old_obj = sender.objects.get(pk=instance.pk)

    except sender.DoesNotExist:
        return False

    for field in instance._meta.fields:
        field_type = field.get_internal_type()
        field_name = field.name

        if (field_type == 'FileField' or field_type == 'ImageField' or field_type == 'ImageSpecField') and field_name != 'title_image':
            origin_file = getattr(old_obj, field_name)
            new_file = getattr(instance, field_name)

            if not origin_file:
                return True

            if origin_file != new_file  and os.path.isfile(origin_file.path):
                os.remove(origin_file.path)
                logger.debug('updating {} field file are replacing  from = {}, to = {} at model of {}'.format(field_type,origin_file,new_file,sender.__name__))



@receiver(pre_save)
def pre_save_handler_for_blog(sender, instance=None, **kwargs):
    list_of_models = ('ProjectPost', 'OnlineStudyPost', 'BlogPost', 'InterestingOpenSourcePost', 'BooksPost')
    if sender.__name__ in list_of_models: # this is the dynamic part you want
        get_title_image_url_in_textfield(instance)
        auto_delete_file_on_save_for_blog(sender, instance)





@receiver(post_delete)
def auto_delete_file_on_delete_for_blog(sender, instance=None, **kwargs):
    list_of_models = ('ProjectPost', 'OnlineStudyPost', 'BlogPost', 'InterestingOpenSourcePost', 'BooksPost')
    if sender.__name__ in list_of_models: # this is the dynamic part you want

        for field in instance._meta.fields:
            field_type = field.get_internal_type()

            if field_type == 'FileField' or field_type == 'ImageField' or field_type == 'ImageSpecField':
                origin_file = getattr(instance, field.name)

                if origin_file == 'title_image':
                    continue

                if origin_file and os.path.isfile(origin_file.path):
                    os.remove(origin_file.path)
                    logger.debug('{} field file is deleted name of {} at model of {}'.format(field_type,origin_file,sender.__name__))