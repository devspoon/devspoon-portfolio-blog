from uuid import uuid4
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from imagekit.models import ImageSpecField  # 썸네일 함수
from imagekit.processors import ResizeToFill  # 사이즈조절

from django.db import models
from django.db.models import F
from django.contrib.auth.models import AbstractUser

from utils.email import *

from utils.os.file_path_name_gen import date_upload_to

# Create your models here.

class UserCustomQuerySet(models.QuerySet):
    def deleted_users(self):
        return self.filter(is_deleted=True)

    def users(self):
        return self.filter(is_deleted=False)

class UserCustomManager(models.Manager):
    def get_queryset(self):
        return UserCustomQuerySet(self.model, using=self._db)

    def deleted_users(self):
        return self.get_queryset().deleted_user()

    def users(self):
        return self.get_queryset().users()

class User(AbstractUser):

    class Gender(models.TextChoices):
        MAN = '0', _('Female')
        WOMAN = '1', _('Male')
        NO_DISCLOSE = '2', _('Not to disclose')

    email = models.EmailField(max_length=200, unique=True, null=True, verbose_name=_('Email')) # it can be null for synchronization of social account
    username = models.CharField(null=False, max_length=30, unique = False, verbose_name=_('User Name'))
    nickname = models.CharField(null=False, max_length=30, verbose_name=_('Nick Name'))
    gender = models.SmallIntegerField(choices = Gender.choices, default=Gender.NO_DISCLOSE, verbose_name=_('Gender'))
    verified = models.BooleanField(default=False, verbose_name=_('Email Verified State'))
    profile_image = models.ImageField(upload_to=date_upload_to, default='default/no_img.png', verbose_name=_('User Profile Image'))
    photo_thumbnail = ImageSpecField(
        source="profile_image",  # 원본 ImageField이름
        processors=[ResizeToFill(500, 325)],  # 사이즈 조정
        format="JPEG",  # 최종 저장 포맷
        options={"quality": 60},  # 저장 옵션
    )

    is_deleted = models.BooleanField(default=False, verbose_name=_('Deleted State'))
    last_login_at = models.DateTimeField(null=True, verbose_name=_('Last Login Time'))
    updated_at = models.DateTimeField(auto_now=True,null=True, verbose_name=_('Updated Time'))
    deleted_at = models.DateTimeField(null=True, verbose_name=_('Deleted Time'))

    object = models.Manager()
    user_objects = UserCustomManager()

    # USERNAME_FIELD은 user model에서 사용할 고유 식별자, 기본은 id
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    class Meta:
        default_manager_name = 'objects'
        db_table = "abstractuser_user"
        verbose_name = ('user')
        verbose_name_plural = ('users')
        ordering = [F('date_joined'),]
        # ordering = [F('date_joined').desc(nulls_last=True)] # Null 밑으로
        # ordering = [F('-date_joined').asc(nulls_last=True)] # Null 상위로
        constraints = [
            models.UniqueConstraint(fields=['email', 'nickname'], name='unique fields of constraint'),
        ]

    def __str__(self):
        return "%s - %s" % (
            self.username,
            self.nickname,
        )

    def get_full_name(self):
        return f'{self.first_name}{self.last_name}'

    get_full_name.short_description = _('Full name')

    def get_short_name(self):
        return self.nickname

    get_short_name.short_description = _('Name')

    def get_absolute_url(self):
        return reverse('') # profile page

    def set_delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.email = ''
        self.username = ''
        self.first_name = ''
        self.last_name = ''
        self.password = ''
        self.deleted_at = timezone.now()
        self.save()

    def set_deactivate(self):
        self.is_active = False
        self.save()


class UserVerification(models.Model):
    class VERIFY_NAME(models.TextChoices):
        EMAIL = '0', _('Email')
        PASSWORD = '1', _('Password')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification', verbose_name=_('User'))
    verify_name = models.SmallIntegerField(choices = VERIFY_NAME.choices, default=VERIFY_NAME.EMAIL, verbose_name=_('Verify Name'))
    key = models.CharField(null=False, max_length=200, unique=True, verbose_name=_('Token Key'))
    sending_result = models.BooleanField(default=False, verbose_name=_('Sending Mail Result'))
    verified = models.BooleanField(default=False, verbose_name=_('Verified State'))
    expired_at = models.DateTimeField(null=True, verbose_name=_('Expired Time'))
    verified_at = models.DateTimeField(null=True, verbose_name=_('Verified Time'))
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=_('Created Time'))

    class Meta:
            db_table = 'user_email_verification'
            verbose_name = _('user email verification')
            verbose_name_plural = _('user email verification')

    def __str__(self):
        return _('UserEmailVerification')
