from django.contrib import admin
from blog.models.blog import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('tag',)
    list_display_links = ['tag',]


admin.site.register(Tag, TagAdmin)