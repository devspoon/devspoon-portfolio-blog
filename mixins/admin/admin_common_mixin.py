class AdminCommonMixin:
    def set_delete(self, request, queryset):
        queryset.update(is_deleted=True)

    def set_activate(self, request, queryset):
        queryset.update(is_deleted=False)

    def set_hidden(self, request, queryset):
        queryset.update(is_hidden=True)

    def set_visible(self, request, queryset):
        queryset.update(is_hidden=False)
