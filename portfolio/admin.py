from django.contrib import admin
from django.contrib.admin import AdminSite
from portfolio.models import Portfolio, PersonalInfo, ProfileSummary, WorkExperience, EducationStudy, InterestedIn, AboutProjects

# Register your models here.
class PortfolioAdminSite(AdminSite):
    site_header = "Portfolio Admin"
    site_title = "Portfolio Admin Portal"
    index_title = "Welcome to Portfolio Admin Portal"

portfolio_admin_site = PortfolioAdminSite(name='portfolio_admin')


class ProfileSummaryInline(admin.TabularInline):
    model = ProfileSummary

class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['id','language','created_at']
    list_display_links = ['id', 'language']
    inlines = [ProfileSummaryInline]
    

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
    list_display = [field.name for field in AboutProjects._meta.get_fields()]
    list_display_links = ['id', 'projectPost']
    list_editable = ('sort_num',)
    raw_id_fields = ["projectPost"]
    
    
portfolio_admin_site.register(Portfolio, PortfolioAdmin)
portfolio_admin_site.register(PersonalInfo, PersonalInfoAdmin)
portfolio_admin_site.register(ProfileSummary, ProfileSummaryAdmin)
portfolio_admin_site.register(WorkExperience, WorkExperienceAdmin)
portfolio_admin_site.register(EducationStudy, EducationStudyAdmin)
portfolio_admin_site.register(InterestedIn, InterestedInAdmin)
portfolio_admin_site.register(AboutProjects, AboutProjectsAdmin)