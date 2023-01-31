from django.utils.translation import gettext_lazy as _
from django.db import models

class ConnectionMethodStats(models.Model):
    win = models.IntegerField(default=0, verbose_name=_('windows'))
    mac = models.IntegerField(default=0, verbose_name=_('mac'))
    iph = models.IntegerField(default=0, verbose_name=_('iphone'))
    android = models.IntegerField(default=0, verbose_name=_('android'))
    oth = models.IntegerField(default=0, verbose_name=_('others'))
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=_('Created Time'))

    class Meta:
        app_label = 'home'
        db_table = 'connection_method_stats'
        verbose_name = _('connection method stats')
        verbose_name_plural = _('connection method stats')
        ordering = ['-created_at']


class ConnectionHardwareStats(models.Model):
    mobile = models.IntegerField(default=0, verbose_name=_('Mobile'))
    tablet = models.IntegerField(default=0, verbose_name=_('Tablet'))
    pc = models.IntegerField(default=0, verbose_name=_('PC'))
    bot = models.IntegerField(default=0, verbose_name=_('Bot'))
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=_('Created Time'))
    
    class Meta:
        app_label = 'home'
        db_table = 'connection_hardware_stats'
        verbose_name = _('connection hardware stats')
        verbose_name_plural = _('connection hardware stats')
        ordering = ['-created_at']