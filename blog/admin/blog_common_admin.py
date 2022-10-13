from django.contrib import admin
from blog.models.blog import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('tag',)
    print('list_display : ',list_display)
    list_display_links = ['tag',]


admin.site.register(Tag, TagAdmin)