from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.contrib.admin import AdminSite

from .views.admin_email_login_forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, UserProfile, SendingEmailMonitor, PolicyPages

class UserAdminSite(AdminSite):
    site_header = "User Admin"
    site_title = "User Admin Portal"
    index_title = "Welcome to User Admin Portal"

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        ordering = {
            "Users": 1,
            "User profile": 2,
            "Sending email monitor": 3,
            "Policy pages": 4
        }
        app_dict = self._build_app_dict(request)
        # a.sort(key=lambda x: b.index(x[0]))
        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: ordering[x['name']])

        return app_list

user_admin_site = UserAdminSite(name='user_admin')

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
        ('key information', {'fields': ['username', 'email', 'password', 'nickname','gender']}),
        ('detail information', {'fields': ['date_joined', 'last_login_at', 'last_login','verified', 'is_superuser', 'is_staff', 'is_active','is_privacy_policy', 'is_terms_of_service', 'is_mobile_authentication', 'is_deleted']}),
        ('more information', {'fields': ['profile_image', 'deleted_at']}),
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

user_admin_site.register(User, CustomUserAdmin)
user_admin_site.register(UserProfile, UserProfileAdmin)
user_admin_site.register(SendingEmailMonitor, SendingEmailMonitorAdmin)
user_admin_site.register(PolicyPages, PagesAdmin)