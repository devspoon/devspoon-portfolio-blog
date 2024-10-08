from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete
from django.urls import reverse

from django.db.models import F
from django.db import transaction

from django.db import models

class BoardReplyMixin(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField(default='', blank=False, verbose_name=_('Comment'))
    depth = models.SmallIntegerField(default=0, verbose_name=_('Reply depth'))
    group = models.SmallIntegerField(default=0, verbose_name=_('Reply group'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='parent_set' , null=True, blank=True, default = None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.comment


class NoticeReply(BoardReplyMixin):
    board = models.ForeignKey('board.Notice', on_delete=models.CASCADE)

    class Meta:
        db_table = 'notice_board_reply'
        verbose_name = _('notice board reply')
        verbose_name_plural = _('notice board reply')
        ordering = [('group'),]


class VisiterReply(BoardReplyMixin):
    board = models.ForeignKey('board.Visiter', on_delete=models.CASCADE)

    class Meta:
        db_table = 'visiter_board_reply'
        verbose_name = _('visiter board reply')
        verbose_name_plural = _('visiter board reply')
        ordering = [('group'),]


class ReactivationReply(BoardReplyMixin):
    board = models.ForeignKey('board.Reactivation', on_delete=models.CASCADE)

    class Meta:
        db_table = 'reactivation_board_reply'
        verbose_name = _('reactivation board reply')
        verbose_name_plural = _('reactivation board reply')
        ordering = [('group'),]


@receiver(post_delete)
def auto_delete_file_on_delete_for_board(sender, instance=None, **kwargs):
    list_of_models = ('NoticeReply', 'VisiterReply', 'ReactivationReply')
    if sender.__name__ in list_of_models: # this is the dynamic part you want

        with transaction.atomic():
            board = sender.objects.get(pk=instance.pk).board

            if board.reply_count > 0 :
                board.reply_count = F('reply_count') - 1
                board.save()
