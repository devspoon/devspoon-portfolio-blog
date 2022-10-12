import logging
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from django.db import models
from django.db.models import Q

logger = logging.getLogger(__name__)


class ActivateDataQuerySet(models.QuerySet):
    def deleted_data(self):
        return self.filter(is_deleted=True)

    def hidden_data(self):
        return self.filter(Q(is_deleted=False) & Q(is_hidden=True))

    def deleted_hidden_data(self):
        return self.filter(Q(is_deleted=True) & Q(is_hidden=True))

    def data(self):
        return self.filter(Q(is_deleted=False) & Q(is_hidden=False))

class ActivateDataManager(models.Manager):
    def get_queryset(self):
        return ActivateDataQuerySet(self.model, using=self._db)

    def get_deleted_data(self):
        return self.get_queryset().deleted_data()

    def get_hidden_data(self):
        return self.get_queryset().hidden_data()

    def get_deleted_hidden_user(self):
        return self.get_queryset().deleted_hidden_data()

    def get_data(self):
        return self.get_queryset().data()


class Board(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Author'))
    title = models.CharField(max_length=200, blank=False, verbose_name=_('Title'))
    content = models.TextField(blank=False, verbose_name=_('Content'))
    table_name = models.CharField(default=__name__, max_length=30, blank=True, verbose_name=_('table_name'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reply_count = models.IntegerField(default=0, verbose_name=_('Reply Count'))
    last_group_num = models.IntegerField(default=0, verbose_name=_('Reply last group id'))
    visit_count = models.PositiveIntegerField(default=0, verbose_name=_('Visit Count'))

    is_deleted = models.BooleanField(default=False, verbose_name=_('Deleted state'))
    is_hidden = models.BooleanField(default=False, verbose_name=_('Hidden state'))

    objects = models.Manager()
    activate_objects = ActivateDataManager()

    class Meta:
        abstract = True
        default_manager_name = 'objects'

    def __str__(self):
        return self.title


class Notice(Board):
    priority = models.SmallIntegerField(default=0, verbose_name=_('Priority')) # it can made to access other board
    sorting_sequence = models.SmallIntegerField(default=0, verbose_name=_('Sorting sequence')) # Set the print order on each board
    class Meta:
        default_manager_name = 'objects'
        db_table = 'notice_board'
        verbose_name = _('notice')
        verbose_name_plural = _('notice')
        ordering = ['-created_at']

    def get_absolute_url(self):
        print('Notice !!!! ')
        return reverse('board:notice_detail', kwargs={'pk':self.pk} )



class Visiter(Board):
    class Meta:
        default_manager_name = 'objects'
        db_table = 'visiter_board'
        verbose_name = _('visiter')
        verbose_name_plural = _('visiter')
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('board:notice_detail', kwargs={'pk':self.pk} )


class Reactivation(Board):
    class Meta:
        default_manager_name = 'objects'
        db_table = 'reactuvation_board'
        verbose_name = _('reactivation')
        verbose_name_plural = _('reactivation')
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('board:notice_detail', kwargs={'pk':self.pk} )