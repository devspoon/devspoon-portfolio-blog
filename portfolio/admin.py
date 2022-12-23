from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.safestring import mark_safe
from portfolio.models import Portfolio, PersonalInfo, ProfileSummary, WorkExperience, EducationStudy, InterestedIn, AboutProjects
from blog.models.blog import ProjectPost

# Register your models here.
class PortfolioAdminSite(AdminSite):
    site_header = 'Portfolio Admin'
    site_title = 'Portfolio Admin Portal'
    index_title = 'Welcome to Portfolio Admin Portal'

portfolio_admin_site = PortfolioAdminSite(name='portfolio_admin')


class ProfileSummaryInline(admin.TabularInline):
    model = ProfileSummary

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['id','portfolio_image_1', 'portfolio_image_2', 'portfolio_image_3','language','created_at']
    list_display_links = ['id', 'language', 'created_at']
    fieldsets = [
        ('File Upload', {'fields': ['portfolio_cv_file', 'portfolio_image1', 'portfolio_image_1','portfolio_image2', 'portfolio_image_2','portfolio_image3', 'portfolio_image_3'],'classes': ['collapse']}),
        ('detail information', {'fields': ['language', 'summary']}),
    ]
    readonly_fields = ['portfolio_image_1', 'portfolio_image_2', 'portfolio_image_3', 'created_at']
    inlines = [ProfileSummaryInline]
    
    def portfolio_image_1(self,obj):
        return mark_safe('<img src="{}" style="width:250px;height:150px;"/>'.format(obj.portfolio_image1.url))

    def portfolio_image_2(self,obj):
        return mark_safe('<img src="{}" style="width:250px;height:150px;"/>'.format(obj.portfolio_image2.url))

    def portfolio_image_3(self,obj):
        return mark_safe('<img src="{}" style="width:250px;height:150px;"/>'.format(obj.portfolio_image3.url))

    portfolio_image_1.short_description = 'portfolio_image_preview_1'
    portfolio_image_2.short_description = 'portfolio_image_preview_2'
    portfolio_image_3.short_description = 'portfolio_image_preview_3'
    
class PersonalInfoAdmin(admin.ModelAdmin):
    list_display = ['id','name','created_at']
    list_display_links = ['id', 'name']

    
class ProfileSummaryAdmin(admin.ModelAdmin):
    list_display = ['id','position','skill','created_at']
    list_display_links = ['id', 'position','skill']
    
    
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['id','title','role','sort_num','created_at']
    list_display_links = ['id','title','role']
    list_editable = ('sort_num',)
    
    
class EducationStudyAdmin(admin.ModelAdmin):
    list_display = ['id','title','sort_num','created_at']
    list_display_links = ['id','title','created_at']
    list_editable = ('sort_num',)
    
    
class InterestedInAdmin(admin.ModelAdmin):
    list_display = ['id','title','created_at']
    list_display_links = ['id', 'title']
    
        
class AboutProjectsAdmin(admin.ModelAdmin):
    list_display = ['id','projectpost','sort_num','created_at'] #[field.name for field in AboutProjects._meta.get_fields()]
    list_display_links = ['id', 'projectpost']
    list_editable = ('sort_num',)
    raw_id_fields = ('projectpost',)
    date_hierarchy = 'created_at'


class ProjectPostHiddenAdmin(admin.ModelAdmin):
    def get_model_perms(self, request): #tric regist
        return {}
    

portfolio_admin_site.register(Portfolio, PortfolioAdmin)
portfolio_admin_site.register(PersonalInfo, PersonalInfoAdmin)
portfolio_admin_site.register(ProfileSummary, ProfileSummaryAdmin)
portfolio_admin_site.register(WorkExperience, WorkExperienceAdmin)
portfolio_admin_site.register(EducationStudy, EducationStudyAdmin)
portfolio_admin_site.register(InterestedIn, InterestedInAdmin)
portfolio_admin_site.register(AboutProjects, AboutProjectsAdmin)
portfolio_admin_site.register(ProjectPost,ProjectPostHiddenAdmin)