from django.contrib import admin
from blog.models.blog import BlogPost
from django_summernote.admin import SummernoteModelAdmin
from blog.models.blog_reply import BlogPostReply
from blog.admin.blog_common_admin import blog_admin_site

class BlogPostAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


class BlogPostReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','post']
    list_display_links = ['id', 'author']


blog_admin_site.register(BlogPost, BlogPostAdmin)
blog_admin_site.register(BlogPostReply, BlogPostReplyAdmin)