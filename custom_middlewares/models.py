import logging

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(getattr(settings, "COMMON_LOGGER", "django"))


class DailyStatsMixin(models.Model):
    """일자 단위 집계 테이블 공통 필드.

    `created_at`은 row가 처음 만들어진 시각일 뿐 집계키가 아니다.
    집계키는 `stat_date`이고 유니크 제약으로 같은 날짜 중복 row를 DB가 막는다.

    `stat_date`가 nullable인 이유:
    이 프로젝트는 migration 파일을 저장소에 두지 않는다(.gitignore). 기존 운영
    테이블에 not-null unique 컬럼을 한 번에 추가하면 모든 기존 row가 같은 기본값을
    받아 유니크 제약에 걸린다. nullable로 추가한 뒤
    `manage.py dedupe_connection_stats`로 중복 합산과 backfill을 수행한다.
    """

    stat_date = models.DateField(
        null=True,
        blank=True,
        unique=True,
        verbose_name=_("Stat Date"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, null=False, verbose_name=_("Created Time")
    )

    class Meta:
        abstract = True


class ConnectionMethodStats(DailyStatsMixin):
    win = models.IntegerField(default=0, verbose_name=_("windows"))
    mac = models.IntegerField(default=0, verbose_name=_("mac"))
    iph = models.IntegerField(default=0, verbose_name=_("iphone"))
    android = models.IntegerField(default=0, verbose_name=_("android"))
    oth = models.IntegerField(default=0, verbose_name=_("others"))

    COUNTER_FIELDS = ("win", "mac", "iph", "android", "oth")

    class Meta:
        app_label = "home"
        db_table = "connection_method_stats"
        verbose_name = _("connection method stats")
        verbose_name_plural = _("connection method stats")
        ordering = ["-stat_date"]


class ConnectionHardwareStats(DailyStatsMixin):
    mobile = models.IntegerField(default=0, verbose_name=_("Mobile"))
    tablet = models.IntegerField(default=0, verbose_name=_("Tablet"))
    pc = models.IntegerField(default=0, verbose_name=_("PC"))
    bot = models.IntegerField(default=0, verbose_name=_("Bot"))

    COUNTER_FIELDS = ("mobile", "tablet", "pc", "bot")

    class Meta:
        app_label = "home"
        db_table = "connection_hardware_stats"
        verbose_name = _("connection hardware stats")
        verbose_name_plural = _("connection hardware stats")
        ordering = ["-stat_date"]
