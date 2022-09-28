from django.contrib import admin
from blog.models.boards import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Tag._meta.get_fields()]
    list_display_links = ['tag']


admin.site.register(Tag, TagAdmin)