from django.contrib import admin
from blog.models.blog import BooksPost
from django_summernote.admin import SummernoteModelAdmin
from blog.models.blog_reply import BooksPostReply
from blog.admin.blog_common_admin import blog_admin_site


class BooksPostAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


class BooksPostReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','post']
    list_display_links = ['id', 'author']


blog_admin_site.register(BooksPost, BooksPostAdmin)
blog_admin_site.register(BooksPostReply, BooksPostReplyAdmin)