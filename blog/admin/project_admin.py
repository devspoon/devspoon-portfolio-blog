from django.contrib import admin
from blog.models.blog import ProjectPost
from django_summernote.admin import SummernoteModelAdmin
from blog.models.blog_reply import ProjectPostReply
from blog.admin.blog_common_admin import blog_admin_site


class ProjectPostAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


class ProjectPostReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','post']
    list_display_links = ['id', 'author']


blog_admin_site.register(ProjectPost, ProjectPostAdmin)
blog_admin_site.register(ProjectPostReply, ProjectPostReplyAdmin)