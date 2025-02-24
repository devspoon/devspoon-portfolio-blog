import logging

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from blog.models.blog import ProjectPost
from utils.os.file_path_name_gen import (
    date_upload_to_for_file,
    date_upload_to_for_image,
)

# Create your models here.
logger = logging.getLogger(getattr(settings, "PORTFOLIO_LOGGER", "django"))


class PortfolioMixin(models.Model):
    class Languages(models.TextChoices):
        KOREAN = "0", _("ko")
        ENGLISH = "1", _("en")

    language = models.CharField(
        blank=False,
        max_length=15,
        choices=Languages.choices,
        default=Languages.KOREAN,
        verbose_name=_("Language"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, null=False, verbose_name=_("Created Time")
    )

    class Meta:
        abstract = True


class Portfolio(PortfolioMixin):
    portfolio_cv_file = models.FileField(
        blank=True,
        upload_to=date_upload_to_for_file,
        verbose_name=_("Portfolio CV File"),
    )
    portfolio_image1 = models.ImageField(
        blank=True,
        upload_to=date_upload_to_for_image,
        default="default/no_img.png",
        verbose_name=_("Portfolio Image1"),
    )
    portfolio_image2 = models.ImageField(
        blank=True,
        upload_to=date_upload_to_for_image,
        default="default/no_img.png",
        verbose_name=_("Portfolio Image2"),
    )
    portfolio_image3 = models.ImageField(
        blank=True,
        upload_to=date_upload_to_for_image,
        default="default/no_img.png",
        verbose_name=_("Portfolio Image3"),
    )
    summary = models.TextField(blank=True, verbose_name=_("Summary"))

    class Meta:
        db_table = "portfolio"
        verbose_name = _("portfolio")
        verbose_name_plural = _("portfolio")

    def __str__(self):
        return "%s" % (self.pk)


class PersonalInfo(PortfolioMixin):
    name = models.CharField(max_length=50, blank=False, verbose_name=_("Name"))
    country = models.CharField(max_length=50, blank=False, verbose_name=_("Country"))
    country_code_regex = RegexValidator(regex=r"^\+([0-9]{2,3})$")
    country_code = models.CharField(
        validators=[country_code_regex],
        max_length=10,
        blank=True,
        default="+82",
        verbose_name=_("Country Phone Code"),
    )
    phone_number_regex = RegexValidator(
        regex=r"^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$"
    )
    phone_number = models.CharField(
        validators=[phone_number_regex],
        max_length=16,
        unique=True,
        blank=True,
        verbose_name=_("Phone Number"),
    )
    office_phone_number = models.CharField(
        max_length=16, unique=True, blank=True, verbose_name=_("Office Phone Number")
    )
    office_email = models.EmailField(
        max_length=128, unique=True, blank=True, verbose_name=_("Office Email")
    )
    office_twitter = models.URLField(blank=True, verbose_name=_("Office Twitter"))
    office_facebook = models.URLField(blank=True, verbose_name=_("Office Facebook"))
    office_instragram = models.URLField(blank=True, verbose_name=_("Office Instagram"))
    office_youtube = models.URLField(blank=True, verbose_name=_("Office Youtube"))
    get_in_touch = models.BooleanField(default=True, verbose_name=_("Get In Touch"))

    class Meta:
        db_table = "personal_info"
        verbose_name = _("personal info")
        verbose_name_plural = _("personal info")
        constraints = [
            models.UniqueConstraint(
                fields=["name", "phone_number", "office_email"],
                name="unique personalinfo",
            )
        ]

    def __str__(self):
        return "%s" % (self.name)


class PortfolioSummary(PortfolioMixin):
    class Position(models.TextChoices):
        FRONT_END = "0", _("Front-End")
        BACK_END = "1", _("Back-End")
        MARKETING = "2", _("Marketing")
        STARTUP = "3", _("Startup")
        MEMBER = "4", _("Member")

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="portfolio_summary",
        verbose_name=_("Portfolio"),
    )
    sort_num = models.IntegerField(
        blank=False, default=0, verbose_name=_("Sort Number")
    )
    position = models.CharField(
        blank=False,
        max_length=15,
        choices=Position.choices,
        default=Position.BACK_END,
        verbose_name=_("Position"),
    )
    content = models.TextField(blank=False, verbose_name=_("Content"))
    skill = models.CharField(
        blank=False,
        max_length=300,
        verbose_name=_("Skill"),
        help_text="Insert skill using comma(,)",
    )

    class Meta:
        db_table = "portfolio_summary"
        verbose_name = _("portfolio summary")
        verbose_name_plural = _("portfolio summary")
        ordering = [
            ("sort_num"),
        ]

    def __str__(self):
        return "%s" % (self.position)


class WorkExperience(PortfolioMixin):
    class Role(models.TextChoices):
        STARTUP_CEO = "0", _("Startup CEO")
        PROJECT_MANAGER = "1", _("Project Manager")
        PROJECT_LEADER = "2", _("Project Leader")
        PROJECT_ASSITANT = "3", _("Project Assistant")
        MARKETER = "4", _("Marketer")
        MEMBER = "5", _("Member")
        OWNER = "6", _("Owner")

    class Color(models.TextChoices):
        PINK = "0", "pink"
        RED = "1", "red"
        ORANGE = "2", "orange"
        YELLOW = "3", "yellow"
        BLUE = "4", "blue"
        SKYBLUE = "5", "skyblue"
        GREEN = "6", "green"
        GRAY = "7", "gray"

    project_start_date = models.DateTimeField(
        null=False, verbose_name=_("Project Start Date")
    )
    project_end_date = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Project End Date")
    )
    sort_num = models.IntegerField(
        blank=False, default=0, verbose_name=_("Sort Number")
    )
    title = models.TextField(blank=False, verbose_name=_("Title"))
    role = models.CharField(
        blank=False,
        max_length=15,
        choices=Role.choices,
        default=Role.PROJECT_MANAGER,
        verbose_name=_("Role"),
    )
    summary = models.TextField(blank=False, verbose_name=_("Summary"))
    content = models.TextField(blank=False, verbose_name=_("Content"))
    color = models.CharField(
        blank=False,
        max_length=15,
        choices=Color.choices,
        default=Color.PINK,
        verbose_name=_("Color"),
    )

    class Meta:
        db_table = "work_experience"
        verbose_name = _("work experience")
        verbose_name_plural = _("work experience")
        ordering = [
            ("sort_num"),
        ]

    def __str__(self):
        return "%s" % (self.title)


class EducationStudy(PortfolioMixin):
    class TYPE(models.TextChoices):
        EDUCATION = "0", _("Education")
        STUDY = "1", _("Study")

    study_start_date = models.DateTimeField(
        null=False, verbose_name=_("Study Start Date")
    )
    study_end_date = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Study End Date")
    )
    sort_num = models.IntegerField(
        blank=False, default=0, verbose_name=_("Sort Number")
    )
    type = models.CharField(
        blank=False,
        max_length=15,
        choices=TYPE.choices,
        default=TYPE.STUDY,
        verbose_name=_("Type"),
    )
    title = models.TextField(blank=False, verbose_name=_("Title"))
    content = models.TextField(blank=False, verbose_name=_("Content"))
    site_name = models.CharField(blank=True, max_length=50, verbose_name=_("Site Name"))
    class_link = models.URLField(blank=True, verbose_name=_("Site Link"))

    class Meta:
        db_table = "education_study"
        verbose_name = _("education study")
        verbose_name_plural = _("education study")
        ordering = [
            ("sort_num"),
        ]

    def __str__(self):
        return "%s" % (self.title)


class InterestedIn(PortfolioMixin):
    icon = models.CharField(blank=False, max_length=50, verbose_name=_("Icon"))
    title = models.TextField(blank=False, verbose_name=_("Title"))
    content = models.TextField(blank=False, verbose_name=_("Content"))

    class Meta:
        db_table = "interested_in"
        verbose_name = _("interested in")
        verbose_name_plural = _("interested in")

    def __str__(self):
        return "%s" % (self.pk)


class AboutProjects(PortfolioMixin):
    projectpost = models.OneToOneField(
        ProjectPost,
        null=True,
        on_delete=models.CASCADE,
        related_name="about_project",
        verbose_name=_("Project Post"),
    )
    sort_num = models.IntegerField(
        blank=False, default=0, verbose_name=_("Sort Number")
    )

    class Meta:
        db_table = "about_projects"
        verbose_name = _("about projects")
        verbose_name_plural = _("about projects")
        ordering = [
            ("sort_num"),
        ]

    def __str__(self):
        return "%s" % (self.pk)


class GetInTouchLog(PortfolioMixin):
    name = models.CharField(blank=False, max_length=300, verbose_name=_("Name"))
    state = models.BooleanField(blank=False, default=True, verbose_name=_("State"))
    email = models.EmailField(max_length=128, blank=False, verbose_name=_("Email"))
    phone_number_regex = RegexValidator(
        regex=r"^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$"
    )
    phone_number = models.CharField(
        validators=[phone_number_regex],
        max_length=16,
        blank=True,
        verbose_name=_("Phone Number"),
    )
    subject = models.CharField(blank=False, max_length=300, verbose_name=_("Subject"))
    message = models.TextField(blank=False, verbose_name=_("Message"))

    class Meta:
        db_table = "get_in_touch"
        verbose_name = _("get in touch")
        verbose_name_plural = _("get in touch")
        ordering = [
            ("-created_at"),
        ]

    def __str__(self):
        return "%s : %s" % (self.name, self.email)
