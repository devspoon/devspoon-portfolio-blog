from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from django.urls import reverse

from django.db import models

# Create your models here.


class MainMenu(models.Model):

    class MenuType(models.TextChoices):
        ADMIN_PAGE = '0', _('adminpage')
        MAIN_PAGE = '1', _('mainpage')
        LIST_PAGE = '2', _('listpage')
        DETAIL_PAGE = '3', _('detailpage')
        USER_PAGE = '4', _('userpage')

    menu_code = models.CharField(max_length=255, blank=False, verbose_name=_(''))
    menu_name = models.CharField(max_length=255, blank=False, verbose_name=_(''))
    menu_icon = models.CharField(max_length=100, blank=True, verbose_name=_(''))
    menu_path = models.CharField(max_length=255, blank=False, verbose_name=_(''))
    menu_type = models.SmallIntegerField(choices = MenuType.choices, default=MenuType.MAIN_PAGE, verbose_name=_('Menu Type'))
    menu_link = models.CharField(max_length=255, blank=True, verbose_name=_(''))
    mene_target = models.CharField(max_length=255, blank=False, default='self', verbose_name=_(''))
    menu_order = models.IntegerField(verbose_name=_(''))
    menu_permit_level = models.IntegerField(verbose_name=_(''))
    menu_side = models.BooleanField(default=True, verbose_name=_(''))
    menu_use = models.BooleanField(default=True, verbose_name=_(''))
    menu_use_nav = models.BooleanField(default=True, verbose_name=_(''))
    menu_created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=_(''))

    class Meta:
            db_table = 'main_menu'
            verbose_name = _('main menu')
            verbose_name_plural = _('main menu')

    def __str__(self):
        return _('MainMenu')


class SiteInfo(models.Model):
    country_number_regex = RegexValidator(regex = r'^+([0-9]{2,3})$')
    country_phone_code = models.CharField(validators = [country_number_regex], max_length = 3, blank=True, default='+82', verbose_name=_(''))
    phone_number_regex = RegexValidator(regex = r'^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$')
    phone_number = models.CharField(validators = [phone_number_regex], max_length = 16, unique = True, blank=True, verbose_name=_(''))
    office_phone_number = models.CharField(max_length = 16, unique = True, blank=True, verbose_name=_(''))
    email = models.EmailField(max_length=128, unique = True, blank=True, verbose_name=_(''))

    class Meta:
            db_table = 'site_info'
            verbose_name = _('site info')
            verbose_name_plural = _('site info')

    def __str__(self):
        return _('SiteInfo')


class WorldSocialAccount(models.Model):
    twitter = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    facebook = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    instragram = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    youtube = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    pinterest = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    linkedin = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    xing = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    meetup = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    opportunity = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    connect = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    upwork = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    freelancer = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    indeed = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    monster = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    angel = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    peoplenjob = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))

    class Meta:
            db_table = 'world_social_account'
            verbose_name = _('world social account')
            verbose_name_plural = _('world social accounts')

    def __str__(self):
        return _('WorldSocialAccount')


class LocalSocialAccount(models.Model):
    wanted = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    rocketpunch = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    remember = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    monster = models.CharField(max_length = 50, unique = True, blank=True, verbose_name=_(''))
    class Meta:
            db_table = 'local_social_account'
            verbose_name = _('local social account')
            verbose_name_plural = _('local social account')

    def __str__(self):
        return _('LocalSocialAccount')