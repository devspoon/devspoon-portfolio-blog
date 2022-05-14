from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from django.urls import reverse

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from users.models import User

# Create your models here.

# header info
class MainMenu(MPTTModel):

    class MenuType(models.TextChoices):
        ADMIN_PAGE = '0', _('admin page')
        MAIN_PAGE = '1', _('main page')
        LIST_PAGE = '2', _('list page')
        DETAIL_PAGE = '3', _('detail page')
        USER_PAGE = '4', _('user page')

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE, verbose_name=_('Parent'))
    menu_name = models.CharField(max_length=255, blank=False, verbose_name=_('Menu Name'))
    menu_icon = models.CharField(max_length=100, blank=True, verbose_name=_('Menu Icon'))
    menu_path = models.CharField(max_length=255, blank=False, verbose_name=_('Menu Path'))
    menu_type = models.CharField(max_length=15, choices = MenuType.choices, default=MenuType.MAIN_PAGE, verbose_name=_('Menu Type'))
    menu_slug = models.SlugField(blank=True, verbose_name=_('Menu Slug'))
    menu_link = models.URLField(blank=True, verbose_name=_('Menu Link'))
    menu_target = models.CharField(max_length=255, blank=False, default='_self', verbose_name=_('Menu Target'))
    menu_permit_level = models.IntegerField(default=0,verbose_name=_('Menu Permit Level'))
    menu_side = models.BooleanField(default=True, verbose_name=_('Menu Side'))
    menu_use = models.BooleanField(default=True, verbose_name=_('Menu Use'))
    menu_use_nav = models.BooleanField(default=True, verbose_name=_('Menu Use Nav'))
    menu_created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=_('Menu Created Time'))
    menu_update_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Menu Updated Time'))

    class MPTTMeta:
        order_insertion_by = ['menu_name']
        
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['parent', 'menu_slug', 'menu_name'], name='MainMenu unique fields of constraint'),
        ]
        db_table = 'main_menu'
        verbose_name = _('main menu')
        verbose_name_plural = _('main menu')
        app_label = "blog"

    def get_slug_list(self):
        try:
            ancestors = self.get_ancestors(include_self=True)
        except:
            ancestors = list()
        else:
            ancestors = [i.menu_slug for i in ancestors]
        slugs = list()
        for i in range(len(ancestors)):
            slugs.append('/'.join(ancestors[:i+1]))
        return slugs
    
    def __str__(self):
        return "%s " % (self.menu_name)

    def get_absolute_url(self):
        ...
        #return reverse('blog:category', kwargs={'slug': self.slug, 'id': self.id})

# footer info
class SiteInfo(models.Model):
    class Language(models.TextChoices):
        ENGLISH = '0', _('Eng')
        KOREAN = '1', _('Kor')        

    site_name = models.CharField(max_length=255, blank=False, verbose_name=_('Site Name'))
    site_owner = models.CharField(max_length=255, blank=False, verbose_name=_('Site Owner'))
    country_code_regex = RegexValidator(regex = r'^\+([0-9]{2,3})$')
    country_code = models.CharField(validators = [country_code_regex], max_length = 3, blank=True, default='+82', verbose_name=_('Country Phone Code'))
    phone_number_regex = RegexValidator(regex = r'^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$')
    phone_number = models.CharField(validators = [phone_number_regex], max_length = 16, unique = True, blank=True, verbose_name=_('Phone Number'))
    office_phone_number = models.CharField(max_length = 16, unique = True, blank=True, verbose_name=_('Office Phone Number'))
    office_email = models.EmailField(max_length=128, unique = True, blank=True, verbose_name=_('Office Email'))
    office_twitter = models.URLField(blank=True, verbose_name=_('Office Twitter'))
    office_facebook = models.URLField(blank=True, verbose_name=_('Office Facebook'))
    office_instragram = models.URLField(blank=True, verbose_name=_('Office Instragram'))
    office_youtube = models.URLField(blank=True, verbose_name=_('Office Youtube'))
    national_language = models.CharField(blank=True, max_length=10, choices = Language.choices, default=Language.ENGLISH, verbose_name=_('National Language'))

    class Meta:
        db_table = 'site_info'
        verbose_name = _('site info')
        verbose_name_plural = _('site info')
        app_label = "blog"

    def __str__(self):
        return "%s" % (self.phone_number)


# Overseas SNS, Portfolio personal page url
class WorldSocialAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='world_social_account', verbose_name=_('User'))
    twitter = models.URLField(blank=True, verbose_name=_('twitter'))
    facebook = models.URLField(blank=True, verbose_name=_('facebook'))
    instragram = models.URLField(blank=True, verbose_name=_('instragram'))
    youtube = models.URLField(blank=True, verbose_name=_('youtube'))
    pinterest = models.URLField(blank=True, verbose_name=_('pinterest'))
    linkedin = models.URLField(blank=True, verbose_name=_('linkedin'))
    xing = models.URLField(blank=True, verbose_name=_('xing'))
    meetup = models.URLField(blank=True, verbose_name=_('meetup'))
    opportunity = models.URLField(blank=True, verbose_name=_('opportunity'))
    connect = models.URLField(blank=True, verbose_name=_('connect'))
    upwork = models.URLField(blank=True, verbose_name=_('upwork'))
    freelancer = models.URLField(blank=True, verbose_name=_('freelancer'))
    indeed = models.URLField(blank=True, verbose_name=_('indeed'))
    monster = models.URLField(blank=True, verbose_name=_('monster'))
    angel = models.URLField(blank=True, verbose_name=_('angel'))
    peoplenjob = models.URLField(blank=True, verbose_name=_('peoplenjob'))

    class Meta:
        db_table = 'world_social_account'
        verbose_name = _('world social account')
        verbose_name_plural = _('world social accounts')
        app_label = "blog"

    def __str__(self):
        return "%s" % (self.id)


# Local SNS, Portfolio personal page url
class LocalSocialAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='local_social_account', verbose_name=_('User'))
    wanted = models.URLField(blank=True, verbose_name=_('wanted'))
    rocketpunch = models.URLField(blank=True, verbose_name=_('rocketpunch'))
    remember = models.URLField(blank=True, verbose_name=_('remember'))
    monster = models.URLField(blank=True, verbose_name=_('monster'))
    class Meta:
        db_table = 'local_social_account'
        verbose_name = _('local social account')
        verbose_name_plural = _('local social account')
        app_label = "blog"

    def __str__(self):
        return "%s" % (self.id)