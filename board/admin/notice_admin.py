from django.contrib import admin
from board.models.board import Notice
from django_summernote.admin import SummernoteModelAdmin
#from blog.models.blog_reply import BlogPostReply

class NoticeBoardAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


# @admin.register(BlogPostReply)
# class BlogPostReplyAdmin(admin.ModelAdmin):
#     list_display = ['id','author','post']
#     list_display_links = ['id', 'author']


admin.site.register(Notice, NoticeBoardAdmin)