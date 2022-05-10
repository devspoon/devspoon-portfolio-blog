from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .views.admin_email_login_forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, UserProfile, SendingEmailMonitor, PolicyPages

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    # list_display = ['email', 'username',]

    def profile_thumbnail(self, obj):
        return mark_safe('<img src="{}"/>'.format(obj.photo_thumbnail.url))

    profile_thumbnail.short_description = 'profile_thumbnail'

    list_display = ('id', 'username', 'email', 'profile_thumbnail')
    fieldsets = [
        ('주요정보', {'fields': ['username', 'email', 'nickname','gender']}),
        ('상세정보', {'fields': ['date_joined', 'last_login_at', 'last_login','verified', 'is_superuser', 'is_staff', 'is_active','is_privacy_policy', 'is_terms_of_service', 'is_mobile_authentication', 'is_deleted']}),
        ('기타정보', {'fields': ['profile_image', 'deleted_at']}),
    ]
    list_display_links = ['id', 'username', 'email']

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "nickname", "point", "email_notifications")
    list_display_links = ['id', 'user', 'nickname']


class SendingEmailMonitorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SendingEmailMonitor._meta.get_fields()]
    list_display_links = ['id', 'vendor']


class PagesAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    list_display_links = ['id', 'title']

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(SendingEmailMonitor, SendingEmailMonitorAdmin)
admin.site.register(PolicyPages, PagesAdmin)