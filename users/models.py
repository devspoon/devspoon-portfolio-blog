import logging
import os
import shutil
from uuid import uuid4
from datetime import datetime
from django.utils.dateformat import DateFormat

from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField  # 썸네일 함수
from imagekit.processors import ResizeToFill  # 사이즈조절

from utils.email import *
from utils.os.file_path_name_gen import date_upload_to_for_image

# Create your models here.

logger = logging.getLogger(getattr(settings, "USERS_LOGGER", "django"))


class UserCustomQuerySet(models.QuerySet):
    def deleted_users(self):
        return self.filter(is_deleted=True)

    def users(self):
        return self.filter(is_deleted=False)


class UserCustomManager(models.Manager):
    def get_queryset(self):
        return UserCustomQuerySet(self.model, using=self._db)

    def get_deleted_users(self):
        return self.get_queryset().deleted_users()

    def get_users(self):
        return self.get_queryset().users()


class User(AbstractUser):
    class Gender(models.TextChoices):
        MAN = "0", _("Female")
        WOMAN = "1", _("Male")
        NO_DISCLOSE = "2", _("Not to disclose")

    email = models.EmailField(
        max_length=200, null=True, verbose_name=_("Email")
    )  # it can be null for synchronization of social account
    notification_email = models.EmailField(
        max_length=200,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Notification Email"),
    )
    username = models.CharField(null=False, max_length=30, verbose_name=_("User Name"))
    nickname = models.CharField(
        null=False, max_length=30, unique=True, verbose_name=_("Nick Name")
    )
    gender = models.CharField(
        max_length=15,
        choices=Gender.choices,
        default=Gender.NO_DISCLOSE,
        verbose_name=_("Gender"),
    )
    verified = models.BooleanField(
        default=False, verbose_name=_("Email Verified State")
    )
    profile_image = models.ImageField(
        upload_to=date_upload_to_for_image,
        default="default/no_img.png",
        verbose_name=_("User Profile Image"),
    )
    photo_thumbnail = ImageSpecField(
        source="profile_image",  # 원본 ImageField이름
        processors=[ResizeToFill(140, 140)],  # 사이즈 조정
        format="JPEG",  # 최종 저장 포맷
        options={"quality": 100},  # 저장 옵션
    )
    last_login_ipaddress = models.GenericIPAddressField(
        null=False, default="0.0.0.0", verbose_name=_("Last Login IP Address")
    )

    is_privacy_policy = models.BooleanField(
        blank=True, default=True, verbose_name=_("Privacy Policy")
    )
    is_terms_of_service = models.BooleanField(
        blank=True, default=True, verbose_name=_("Terms of Service")
    )
    is_mobile_authentication = models.BooleanField(
        blank=True, default=False, verbose_name=_("Mobile Authentication")
    )
    is_dormant_account = models.BooleanField(
        blank=True, default=False, verbose_name=_("Dormant Account State")
    )
    is_deleted = models.BooleanField(
        blank=True, default=False, verbose_name=_("Deleted State")
    )
    is_site_register = models.BooleanField(
        blank=True, default=False, verbose_name=_("Site Register User")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, null=False, verbose_name=_("Created Time")
    )
    last_login_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Last Login Time")
    )
    updated_at = models.DateTimeField(
        auto_now=True, null=True, verbose_name=_("Updated Time")
    )
    dormant_account_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Dormant Account Time")
    )
    deleted_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Deleted Time")
    )
    password_replacement_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Password Replacement Time")
    )

    objects = UserManager()
    user_objects = UserCustomManager()

    # USERNAME_FIELD은 user model에서 사용할 고유 식별자, 기본은 id
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    class Meta:
        default_manager_name = "objects"
        db_table = "abstractuser_user"
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = [
            ("-date_joined"),
        ]
        # ordering = [F('date_joined').desc(nulls_last=True)] # Null 밑으로
        # ordering = [F('-date_joined').asc(nulls_last=True)] # Null 상위로
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "email",
                    "nickname",
                ],
                name="unique fields of constraint",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "username",
                    "nickname",
                ],
                name="index username and nickname",
            ),
        ]

    def __str__(self):
        # return "%s - %s" % (
        #     self.username,
        #     self.nickname,
        # )
        return "%s" % (self.nickname,)

    def get_full_name(self):
        return f"{self.first_name}{self.last_name}"

    get_full_name.short_description = _("Full name")

    def set_dormant_account(self):
        # self.instance
        # send email
        # save dormant_account user to new table
        # it can recover using user id(pk)
        # this process run by celery
        self.is_dormant_account = True
        # self.email = ""
        # self.username = ""
        # self.nickname = ""
        # self.first_name = ""
        # self.last_name = ""
        # self.password = ""
        self.dormant_account_at = timezone.now()
        self.save()

    def set_delete(self):
        socialaccount = SocialAccount.objects.filter(user=self.pk).first()
        if socialaccount:
            socialaccount.delete()
            auth_email = EmailAddress.objects.filter(user=self.pk).first()
            if auth_email:
                auth_email.delete()
            logger.debug("socialaccount, auth_email are deleted")

        if self.photo_thumbnail.path:
            dir, _ = os.path.split(self.photo_thumbnail.path)
            if os.path.exists(dir):
                shutil.rmtree(dir)

        if self.profile_image:
            self.profile_image.delete()
        self.is_deleted = True
        self.is_active = False
        self.email = ""
        self.username = ""
        self.nickname = ""
        self.first_name = ""
        self.last_name = ""
        self.password = ""
        self.deleted_at = timezone.now()
        self.save()
        self.userprofile.delete()

    def set_deactivate(self):
        self.is_active = False
        self.save()


class UserVerification(models.Model):
    class VERIFY_NAME(models.TextChoices):
        EMAIL = "0", _("Email")
        PASSWORD = "1", _("Password")

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="verification",
        verbose_name=_("User"),
        null=True,
    )
    verify_name = models.SmallIntegerField(
        choices=VERIFY_NAME.choices,
        default=VERIFY_NAME.EMAIL,
        verbose_name=_("Verify Name"),
    )
    key = models.CharField(null=False, max_length=200, verbose_name=_("Token Key"))
    sending_result = models.BooleanField(
        default=False, verbose_name=_("Sending Mail Result")
    )
    verified = models.BooleanField(default=False, verbose_name=_("Verified State"))
    expired_at = models.DateTimeField(null=True, verbose_name=_("Expired Time"))
    verified_at = models.DateTimeField(null=True, verbose_name=_("Verified Time"))
    created_at = models.DateTimeField(
        auto_now_add=True, null=False, verbose_name=_("Created Time")
    )

    class Meta:
        db_table = "user_email_verification"
        verbose_name = _("user email verification")
        verbose_name_plural = _("user email verification")

    def __str__(self):
        return "%s" % (self.user)


class UserRegistHistory(models.Model):
    email = models.EmailField(max_length=200, null=True, verbose_name=_("Email"))
    username = models.CharField(
        null=False, max_length=30, unique=True, verbose_name=_("User Name")
    )
    nickname = models.CharField(null=False, max_length=30, verbose_name=_("Nick Name"))
    ip_address = models.GenericIPAddressField(
        null=False, default="0.0.0.0", verbose_name=_("IP Address")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, null=False, verbose_name=_("Created Time")
    )

    class Meta:
        db_table = "user_register_history"
        verbose_name = _("register history")
        verbose_name_plural = _("register history")
        ordering = [
            ("-created_at"),
        ]
        indexes = [
            models.Index(
                fields=[
                    "email",
                    "username",
                ],
                name="index register history",
            ),
        ]

    def __str__(self):
        return "%s - %s" % (
            self.email,
            self.username,
        )


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="user_profile",
        verbose_name=_("User"),
    )
    nickname = models.CharField(blank=True, unique=True, max_length=30)
    point = models.IntegerField(blank=True, default=0)
    email_notifications = models.BooleanField(blank=True, default=False)

    class Meta:
        db_table = "user_profile"
        verbose_name = _("user profile")
        verbose_name_plural = _("user profile")

    def __str__(self):
        return "%s" % (self.user)


class SendingEmailMonitor(models.Model):
    vendor = models.CharField(max_length=20, blank=False, verbose_name=_("Vendor Name"))
    sending_success_cnt = models.IntegerField(
        blank=True, default=0, verbose_name=_("Sending Success Count")
    )
    sending_failed_cnt = models.IntegerField(
        blank=True, default=0, verbose_name=_("Sending Failed Count")
    )
    sending_total_cnt = models.IntegerField(
        blank=False, default=0, verbose_name=_("Sending Total Count")
    )
    this_month = models.PositiveIntegerField(
        blank=False,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name=_("This Month"),
    )
    last_sending_state = models.BooleanField(
        blank=False, default=False, verbose_name=_("Last Sending State")
    )
    last_success_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Success Time")
    )
    last_failed_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Failed Time")
    )

    class Meta:
        db_table = "sending_email_monitor"
        verbose_name = _("sending email monitor")
        verbose_name_plural = _("sending email monitor")

    def __str__(self):
        return "%s" % (self.vendor)


class PolicyPages(models.Model):
    title = models.CharField(max_length=150, blank=False, verbose_name=_("Page Title"))
    content = models.TextField(blank=False, verbose_name=_("Page Content"))
    slug = models.SlugField(
        max_length=150,
        blank=True,
        unique=True,
        allow_unicode=True,
        db_index=True,
        verbose_name=_("Page Slug"),
    )
    is_necessary_policy = models.BooleanField(
        blank=False, default=True, verbose_name=_("Necessary Policy")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, null=False, verbose_name=_("Created Time")
    )

    class Meta:
        db_table = "policy_pages"
        verbose_name = _("policy pages")
        verbose_name_plural = _("policy pages")

    def __str__(self):
        return "%s" % (self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).

        You can use this hook to intervene, e.g. abort the login by
        raising an ImmediateHttpResponse

        Why both an adapter hook and the signal? Intervening in
        e.g. the flow from within a signal handler is bad -- multiple
        handlers may be active and are executed in undetermined order.
        """
        pass

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        # user.username = user.email[:30]

        if UserRegistHistory.objects.filter(email=user.email).exists():
            return

        if user.email is not None:
            name = user.email.split("@")[0]
            user.username = name
            user.nickname = user.email + "-" + DateFormat(datetime.now()).format("Ymd")

            ip_address = request.META.get("REMOTE_ADDR")
            UserRegistHistory.objects.create(
                email=user.email,
                username=user.username,
                nickname=user.nickname,
                ip_address=ip_address,
            )

        return user


# Overseas SNS, Portfolio personal page url
class WorldSocialAccount(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="world_social_account",
        verbose_name=_("User"),
    )
    twitter = models.URLField(blank=True, verbose_name=_("twitter"))
    facebook = models.URLField(blank=True, verbose_name=_("facebook"))
    instragram = models.URLField(blank=True, verbose_name=_("instagram"))
    youtube = models.URLField(blank=True, verbose_name=_("youtube"))
    pinterest = models.URLField(blank=True, verbose_name=_("pinterest"))
    linkedin = models.URLField(blank=True, verbose_name=_("linkedin"))
    xing = models.URLField(blank=True, verbose_name=_("xing"))
    meetup = models.URLField(blank=True, verbose_name=_("meetup"))
    opportunity = models.URLField(blank=True, verbose_name=_("opportunity"))
    connect = models.URLField(blank=True, verbose_name=_("connect"))
    upwork = models.URLField(blank=True, verbose_name=_("upwork"))
    freelancer = models.URLField(blank=True, verbose_name=_("freelancer"))
    indeed = models.URLField(blank=True, verbose_name=_("indeed"))
    monster = models.URLField(blank=True, verbose_name=_("monster"))
    angel = models.URLField(blank=True, verbose_name=_("angel"))
    peoplenjob = models.URLField(blank=True, verbose_name=_("peoplenjob"))

    class Meta:
        db_table = "world_social_account"
        verbose_name = _("world social account")
        verbose_name_plural = _("world social accounts")

    def __str__(self):
        return "%s" % (self.user__username)


# Local SNS, Portfolio personal page url
class LocalSocialAccount(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="local_social_account",
        verbose_name=_("User"),
    )
    wanted = models.URLField(blank=True, verbose_name=_("wanted"))
    rocketpunch = models.URLField(blank=True, verbose_name=_("rocketpunch"))
    remember = models.URLField(blank=True, verbose_name=_("remember"))
    monster = models.URLField(blank=True, verbose_name=_("monster"))

    class Meta:
        db_table = "local_social_account"
        verbose_name = _("local social account")
        verbose_name_plural = _("local social account")

    def __str__(self):
        return "%s" % (self.user__username)


@receiver(post_save, sender=User)
def on_save_user(sender, instance, **kwargs):
    profile = UserProfile.objects.filter(user=instance).first()
    # social_account = SocialAccount.objects.filter(user=instance).first()

    temp_num = 0
    if not profile:
        if instance.nickname:
            nickname = instance.nickname
        else:
            nickname = instance.email.split("@")[0]
            check_nickname = User.objects.filter(
                nickname__icontains=nickname
            ).values_list("username", flat=True)
            if nickname in check_nickname:
                for num in check_nickname:
                    nickname = nickname + str(temp_num + 1)
                    if not nickname in check_nickname:
                        break
        UserProfile.objects.create(user=instance, nickname=nickname, point=0)


def delete_thumbnail(origin_file, instance):
    last_path = str(origin_file).split(".")[0]

    if not instance.photo_thumbnail:
        return True
    thumbnail_path, _ = os.path.split(instance.photo_thumbnail.path)
    origin_path = thumbnail_path.split("images")
    full_path = origin_path[0] + "images/" + last_path
    full_path = full_path.replace("/", "\\")  # for window

    if os.path.exists(full_path):
        shutil.rmtree(full_path)
        logger.debug("delete thumbnail file of {}".format(full_path))

    if os.path.exists(
        thumbnail_path
    ):  # Delete automatically created temporary folders and files
        shutil.rmtree(thumbnail_path)
        logger.debug("delete temporary file of {}".format(thumbnail_path))


@receiver(pre_save, sender=User)
def auto_delete_file_on_save(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_obj = sender.objects.get(pk=instance.pk)

    except sender.DoesNotExist:
        return False

    for field in instance._meta.fields:
        field_type = field.get_internal_type()

        if (
            field_type == "FileField"
            or field_type == "ImageField"
            or field_type == "ImageSpecField"
        ):
            origin_file = getattr(old_obj, field.name)
            new_file = getattr(instance, field.name)

            if not origin_file or origin_file == "default/no_img.png":
                return True

            if origin_file != new_file and os.path.isfile(origin_file.path):
                os.remove(origin_file.path)
                logger.debug(
                    "updating {} field file are replacing  from = {}, to = {}".format(
                        field_type, origin_file, new_file
                    )
                )
                delete_thumbnail(origin_file, instance)


@receiver(post_delete, sender=User)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    for field in instance._meta.fields:
        field_type = field.get_internal_type()

        if (
            field_type == "FileField"
            or field_type == "ImageField"
            or field_type == "ImageSpecField"
        ):
            origin_file = getattr(instance, field.name)

            if origin_file == "default/no_img.png":
                return True

            if origin_file and os.path.isfile(origin_file.path):
                os.remove(origin_file.path)
                logger.debug(
                    "{} field file is deleted name of {}".format(
                        field_type, origin_file
                    )
                )
                delete_thumbnail(origin_file, instance)
