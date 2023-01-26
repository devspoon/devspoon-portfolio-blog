from django.utils.translation import gettext_lazy as _
from django.db import models

class ConnectionMethodStats(models.Model):
    win = models.IntegerField(default=0, verbose_name=_('windows'))
    mac = models.IntegerField(default=0, verbose_name=_('mac'))
    iph = models.IntegerField(default=0, verbose_name=_('iphone'))
    android = models.IntegerField(default=0, verbose_name=_('android'))
    oth = models.IntegerField(default=0, verbose_name=_('others'))

    class Meta:
        app_label = 'home'
        db_table = 'connection_method_stats'
        verbose_name = _('connection method stats')
        verbose_name_plural = _('connection methodstats')
