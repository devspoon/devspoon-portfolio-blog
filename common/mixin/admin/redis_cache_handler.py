import logging

from django.conf import settings
from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from common.cache_invalidation import clear_model, invalidate_queryset

logger = logging.getLogger(getattr(settings, "COMMON_LOGGER", "django"))

# 저장·삭제 때의 캐시 무효화는 모델 시그널이 커밋 뒤에 한다(common/cache_invalidation.py).
# 여기서는 시그널이 걸리지 않는 queryset.update() 액션과 관리자의 수동 캐시 삭제만 다룬다.


class AdminCommonActionMixin:
    def _update(self, queryset, **fields):
        queryset.update(**fields)
        invalidate_queryset(queryset)

    def set_delete(self, request, queryset):
        self._update(queryset, is_deleted=True)

    def set_activate(self, request, queryset):
        self._update(queryset, is_deleted=False)

    def set_hidden(self, request, queryset):
        self._update(queryset, is_hidden=True)

    def set_visible(self, request, queryset):
        self._update(queryset, is_hidden=False)


class _CacheActionsMixin:
    def delete_all_cache(self, request, queryset):
        clear_model(self.model)

    def delete_selected_items(self, request, queryset):
        for obj in queryset:
            obj.delete()  # 시그널이 커밋 뒤에 캐시를 지운다


class AdminCacheCleanMixin(_CacheActionsMixin):
    pass


class AdminCacheCleanFixedKeyMixin(_CacheActionsMixin, SummernoteModelAdmin):
    pass


class AdminCacheCleanPostMixin(_CacheActionsMixin, SummernoteModelAdmin):
    pass


class AdminCacheCleanReplyMixin(_CacheActionsMixin, admin.ModelAdmin):
    pass
