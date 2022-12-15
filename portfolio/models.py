import logging
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from django.db import models
from blog.models.blog import ProjectPost

from utils.os.file_path_name_gen import date_upload_to_for_file

# Create your models here.
logger = logging.getLogger(__name__)

    
class Portfolio(models.Model):
    portfolio_cv_file = models.FileField(blank=False, upload_to=date_upload_to_for_file,  verbose_name=_('User Profile Image'))
    language = models.CharField(max_length=50, blank=False, verbose_name=_('Language'))
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=_('Created Time'))
    
    class Meta:
        db_table = 'portfolio'
        verbose_name = _('portfolio')
        verbose_name_plural = _('portfolio')

    def __str__(self):
        return "%s" % (self.pk)


class PersonalInfo(models.Model):
    name = models.CharField(max_length=50, blank=False, verbose_name=_('Name'))
    country = models.CharField(max_length=50, blank=False, verbose_name=_('Country'))
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
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=_('Created Time'))

    class Meta:
        db_table = 'personal_info'
        verbose_name = _('personal info')
        verbose_name_plural = _('personal info')

    def __str__(self):
        return "%s" % (self.name)
    
    
class ProfileSummary(models.Model):
    class Position(models.TextChoices):
        FRONT_END = '0', _('Front End')
        BACK_END = '1', _('Back End')
        MARKETING = '2', _('Marketing')
        STARTUP = '3', _('Startup')
        
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='portfolio', verbose_name=_('Portfolio'))
    position = models.CharField(blank=False, max_length=15, choices = Position.choices, default=Position.BACK_END, verbose_name=_('Position'))
    content = models.CharField(blank=False, max_length=300,  verbose_name=_('Content'))
    skill = models.CharField(blank=False, max_length=50, verbose_name=_('Skill'),help_text='Insert skill using comma(,)')
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=_('Created Time'))
    
    class Meta:
        db_table = 'profile_summary'
        verbose_name = _('profile summary')
        verbose_name_plural = _('profile summary')

    def __str__(self):
        return "%s" % (self.position)
    
    
class WorkExperience(models.Model):
    class Role(models.TextChoices):
        STARTUP_CEO = '0', _('Startup CEO')
        PROJECT_MANAGER = '1', _('Project Manager')
        PROJECT_LEADER = '2', _('Project Leader')
        PROJECT_ASSITANT = '3', _('Project Assitant')
        MARKETER = '4', _('Marketer')
        
    project_start_date = models.DateTimeField(null=False, verbose_name=_('Project Start Date'))
    project_end_date = models.DateTimeField(null=False, verbose_name=_('Project End Date'))
    sort_num = models.IntegerField(blank=False, default=0, verbose_name=_('Sort Number'))
    title = models.CharField(blank=False, max_length=50, verbose_name=_('Title'))
    role = models.CharField(blank=False, max_length=15, choices = Role.choices, default=Role.PROJECT_MANAGER, verbose_name=_('Role'))
    summary = models.CharField(blank=False, max_length=300, verbose_name=_('Summary'))
    content = models.TextField(blank=False, verbose_name=_('Content'))
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=_('Created Time'))
    
    class Meta:
        db_table = 'work_experience'
        verbose_name = _('work experience')
        verbose_name_plural = _('work experience')

    def __str__(self):
        return "%s" % (self.title)
    
    
class EducationStudy(models.Model):
    study_start_date = models.DateTimeField(null=False, verbose_name=_('Study Start Date'))
    study_end_date = models.DateTimeField(null=False, verbose_name=_('Study End Date'))
    sort_num = models.IntegerField(blank=False, default=0, verbose_name=_('Sort Number'))
    title = models.CharField(blank=False, max_length=50, verbose_name=_('Title'))
    content = models.TextField(blank=False, verbose_name=_('Content'))
    study_link = models.URLField(blank=True, verbose_name=_('Study Link'))
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=_('Created Time'))
    
    class Meta:
        db_table = 'education_study'
        verbose_name = _('education study')
        verbose_name_plural = _('education study')

    def __str__(self):
        return "%s" % (self.title)
    
    
class InterestedIn(models.Model):
    icon = models.CharField(blank=False, max_length=50, verbose_name=_('Icon'))
    title = models.CharField(blank=False, max_length=50, verbose_name=_('Title'))
    content = models.TextField(blank=False, verbose_name=_('Content'))
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=_('Created Time'))
    
    class Meta:
        db_table = 'interested_in'
        verbose_name = _('interested in')
        verbose_name_plural = _('interested in')

    def __str__(self):
        return "%s" % (self.pk)
    
    
class AboutProjects(models.Model):
    projectPost = models.ForeignKey(ProjectPost, null=True, on_delete=models.CASCADE, related_name='projectpost', verbose_name=_('Project Post'))
    sort_num = models.IntegerField(blank=False, default=0, verbose_name=_('Sort Number'))
    created_at = models.DateTimeField(auto_now_add=True, null=False, verbose_name=_('Created Time'))
    
    class Meta:
        db_table = 'about_projects'
        verbose_name = _('about projects')
        verbose_name_plural = _('about projects')

    def __str__(self):
        return "%s" % (self.pk)
    
    