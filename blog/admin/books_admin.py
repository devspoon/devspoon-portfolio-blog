from django.contrib import admin
from blog.models.boards import BooksPost
from django_summernote.admin import SummernoteModelAdmin
from blog.models.reply import BooksPostReply


class BooksPostAdmin(SummernoteModelAdmin):
    list_display = ['id','author','title']
    list_display_links = ['id', 'author','title']
    summernote_fields = ('content',)


@admin.register(BooksPostReply)
class BooksPostReplyAdmin(admin.ModelAdmin):
    list_display = ['id','author','post']
    list_display_links = ['id', 'author']


admin.site.register(BooksPost, BooksPostAdmin)