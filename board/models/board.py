import logging
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from django.db import models

logger = logging.getLogger(__name__)

class Board(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Author'))
    title = models.CharField(max_length=200, blank=False, verbose_name=_('Title'))
    content = models.TextField(blank=False, verbose_name=_('Content'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reply_count = models.IntegerField(default=0, verbose_name=_('Reply Count'))
    last_group_num = models.IntegerField(default=0, verbose_name=_('Reply last group id'))
    visit_count = models.PositiveIntegerField(default=0, verbose_name=_('Visit Count'))

    is_deleted = models.BooleanField(default=False, verbose_name=_('Deleted state'))
    is_hidden = models.BooleanField(default=False, verbose_name=_('Hidden state'))

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Notice(Board):
    priority = models.SmallIntegerField(default=0, verbose_name=_('Priority')) # it can made to access other board
    sorting_sequence = models.SmallIntegerField(default=0, verbose_name=_('Sorting sequence')) # Set the print order on each board
    class Meta:
        db_table = 'board_notice'
        verbose_name = _('notice')
        verbose_name_plural = _('notice')
        ordering = ['-created_at']


class Visiter(Board):
    class Meta:
        db_table = 'board_visiter'
        verbose_name = _('visiter')
        verbose_name_plural = _('visiter')
        ordering = ['-created_at']


class Reactivation(Board):
    class Meta:
        db_table = 'board_reactuvation'
        verbose_name = _('reactivation')
        verbose_name_plural = _('reactivation')
        ordering = ['-created_at']