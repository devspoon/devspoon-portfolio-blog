from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .views.admin_email_login_forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    # list_display = ['email', 'username',]
    list_display = ('id', 'username', 'email')
    fieldsets = [
        ('주요정보', {'fields': ['username', 'email', 'nickname','gender']}),
        ('상세정보', {'fields': ['date_joined', 'last_login_at', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'is_deleted']}),
        ('기타정보', {'fields': ['profile_image', 'deleted_at']}),
    ]

# class UserAdmin(admin.ModelAdmin):
#     list_display = ('id', 'username', 'email')
#     fieldsets = [
#         ('주요정보', {'fields': ['username', 'email', 'nickname','gender']}),
#         ('상세정보', {'fields': ['date_joined', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'is_deleted']}),
#         ('기타정보', {'fields': ['profile_image', 'updated_at', 'deleted_at']}),
#     ]

admin.site.register(User, CustomUserAdmin)
# admin.site.register(User, UserAdmin)