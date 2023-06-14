import logging

from django.conf import settings
from django.contrib import admin
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.utils.decorators import method_decorator
from django_summernote.admin import SummernoteModelAdmin

from common.components.django_redis_cache_components import dredis_cache_delete
from common.decorators.cache import index_cache_clean

logger = logging.getLogger(getattr(settings, "COMMON_LOGGER", "django"))


class AdminCommonAction(object):
    def set_delete(self, request, queryset):
        queryset.update(is_deleted=True)

    def set_activate(self, request, queryset):
        queryset.update(is_deleted=False)

    def set_hidden(self, request, queryset):
        queryset.update(is_hidden=True)

    def set_visible(self, request, queryset):
        queryset.update(is_hidden=False)


class AdminCacheClean(object):
    cache_prefix = ""
    use_pk = True

    def delete_cache(self, prefix: str, pk: int = None):
        if self.use_pk:
            dredis_cache_delete(prefix, pk)
        else:
            dredis_cache_delete(prefix, 0)

    def delete_all_cache(self, request, queryset):
        self.delete_cache(self.cache_prefix)

    def delete_selected_items(self, request, queryset):
        for obj in queryset:
            self.delete_cache(self.cache_prefix, obj.pk)
            obj.delete()

    def save_model(self, request, obj, form, change):
        self.delete_cache(self.cache_prefix, obj.pk)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        self.delete_cache(self.cache_prefix, obj.pk)
        super().delete_model(request, obj)


class AdminCacheCleanFixedKey(AdminCacheClean):
    view_keys = ""

    def delete_cache(self):
        for key in self.view_keys:
            cache.delete(key)

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


class AdminCacheCleanPost(SummernoteModelAdmin):
    cache_reply_prefix = ""
    cache_prefix = ""

    def delete_cache(self, prefix: str, pk: int = None):
        dredis_cache_delete(prefix, pk)

    def delete_all_cache(self, request, queryset):
        self.delete_cache(self.cache_prefix)
        self.delete_cache(self.cache_reply_prefix)

    @method_decorator(index_cache_clean)
    def delete_selected_items(self, request, queryset):
        for obj in queryset:
            self.delete_cache(self.cache_prefix, obj.pk)
            self.delete_cache(self.cache_reply_prefix, obj.pk)
            obj.delete()

    @method_decorator(index_cache_clean)
    def delete_model(self, request, obj):
        self.delete_cache(self.cache_prefix, obj.pk)
        self.delete_cache(self.cache_reply_prefix, obj.pk)
        super().delete_model(request, obj)

    @method_decorator(index_cache_clean)
    def save_model(self, request, obj, form, change):
        self.delete_cache(self.cache_prefix, obj.pk)
        super().save_model(request, obj, form, change)


class AdminCacheCleanReply(admin.ModelAdmin):
    cache_prefix = ""

    def delete_cache(self, prefix: str, pk: int = None):
        dredis_cache_delete(prefix, pk)

    def delete_all_cache(self, request, queryset):
        self.delete_cache(self.cache_prefix)

    def delete_selected_items(self, request, queryset):
        for obj in queryset:
            self.delete_cache(self.cache_prefix, obj.post.pk)
            obj.delete()

    def save_model(self, request, obj, form, change):
        self.delete_cache(self.cache_prefix, obj.post.pk)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        self.delete_cache(self.cache_prefix, obj.post.pk)
        super().delete_model(request, obj)
