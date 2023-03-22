from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key


class AdminCommonAction(object):
    def set_delete(self, request, queryset):
        queryset.update(is_deleted=True)

    def set_activate(self, request, queryset):
        queryset.update(is_deleted=False)

    def set_hidden(self, request, queryset):
        queryset.update(is_hidden=True)

    def set_visible(self, request, queryset):
        queryset.update(is_hidden=False)


class AdminCacheCleanFixedKey(object):
    view_key = ""
    template_key = ""

    def delete_cache(self):
        for key in self.view_key:
            cache.delete(key)
        for key in self.template_key:
            redis_key = make_template_fragment_key(key)
            cache.delete(redis_key)

    def delete_selected_items(self, request, queryset):
        for obj in queryset:
            self.delete_cache()
            obj.delete()

    def delete_all_cache(self, request, queryset):
        self.delete_cache()

    def save_model(self, request, obj, form, change):
        self.delete_cache()
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        self.delete_cache()
        super().delete_model(request, obj)
