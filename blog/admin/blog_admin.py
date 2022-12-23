from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from blog.models.blog import BlogPost, Tag
from blog.models.blog_reply import BlogPostReply
from blog.admin.common_admin import blog_admin_site
from mixins.admin.admin_common_mixin import AdminCommonMixin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from django import forms


class BlogPostAdmin(SummernoteModelAdmin, AdminCommonMixin):
    list_per_page = 20

    list_display = ['id','author','title','is_deleted','is_hidden']
    list_display_links = ['id', 'author','title']
    list_filter = ('author', ('created_at', DateRangeFilter), 'is_deleted', 'is_hidden')
    list_editable = ('is_deleted','is_hidden')
    search_fields = ('author__username', 'title','content')
    summernote_fields = ('content',)
    actions = ['set_delete','set_activate','set_hidden','set_visible']
    filter_horizontal = ('tag_set',)
    date_hierarchy = 'created_at'
    # prepopulated_fields = {'slug' : ['title']}



class BlogPostReplyAdmin(admin.ModelAdmin, AdminCommonMixin):
    list_per_page = 20

    list_display = ['id','author','post']
    list_display_links = ['id', 'author']
    list_filter = ('author', ('created_at', DateRangeFilter))
    search_fields = ('author__username', 'comment')
    actions = ['set_delete','set_activate','set_hidden','set_visible']


blog_admin_site.register(BlogPost, BlogPostAdmin)
blog_admin_site.register(BlogPostReply, BlogPostReplyAdmin)