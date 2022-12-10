from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from django.contrib.admin import SimpleListFilter
from django import forms
from django.contrib import messages

import csv
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.urls import path

from .views.admin_email_login_forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, UserProfile, SendingEmailMonitor, PolicyPages

class NickNameFilter(SimpleListFilter):
    title = 'Nick Name Filter'
    parameter_name = 'user_nickname'

    def lookups(self,request,model_admin):
        return (
            ('has_nickname', 'has_nickname'),
            ('no_nickname', 'no_nickname')
        )

    def queryset(self,request,queryset):
        if not self.value():
            return queryset
        if self.value().lower() == 'has_nickname':
            return queryset.exclude(nickname='')
        if self.value().lower() == 'no_nickname':
            return queryset.filter(nickname='')

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])
        return response

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

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

class UserProfileInline(admin.TabularInline):
    model = UserProfile # OneT

class CustomUserAdmin(UserAdmin, ExportCsvMixin):
    change_list_template = "admin/users_changelist.html"
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_per_page = 20
    # list_display = ['email', 'username',]

    list_display = ('id', 'username', 'email', 'profile_thumbnail','verified','is_site_register','is_active','is_deleted')
    list_editable = ('verified','is_active','is_deleted')
    search_fields = ('username', 'email')
    fieldsets = [
        ('key information', {'fields': ['username', 'email', 'password', 'nickname','gender'],'classes': ['collapse']}),
        ('detail information', {'fields': ['date_joined', 'last_login_at', 'last_login','verified', 'is_superuser', 'is_staff', 'is_active','is_privacy_policy', 'is_terms_of_service', 'is_mobile_authentication', 'is_deleted'],'classes': ['collapse']}),
        ('more information', {'fields': ['profile_image', 'deleted_at'],'classes': ['collapse']}),
    ]
    list_display_links = ['id', 'username', 'email']
    list_filter = (
        ('updated_at', DateRangeFilter),('dormant_account_at', DateRangeFilter),('deleted_at', DateRangeFilter),NickNameFilter, 'is_dormant_account', 'is_deleted','is_site_register'
    )
    actions = ["set_delete","set_activate","set_dormant_account","set_activated_account","dormant_account_at","export_as_csv"]
    readonly_fields = ["is_mobile_authentication","is_site_register"]
    inlines = [UserProfileInline]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]

            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)

            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")

            for index, value in enumerate(csv_data):
                if index is 0 :
                    continue
                data = value.split(",")
                if len(data) <= 1:
                    break
                fields = []
                for i in data:
                    temp = i.replace("TRUE","True").replace("FALSE","False")
                    fields.append(temp)
                try:
                    created = User.objects.update_or_create(
                        email = fields[9],
                        defaults={
                            'password':fields[1],
                            'last_login':fields[2],
                            'is_superuser':fields[3],
                            'first_name':fields[4],
                            'last_name':fields[5],
                            'is_staff':fields[6],
                            'is_active':fields[7],
                            'date_joined':fields[8],
                            'email':fields[9],
                            'username':fields[10],
                            'nickname':fields[11],
                            'gender':fields[12],
                            'verified':fields[13],
                            'profile_image':fields[14],
                            'is_privacy_policy':fields[15],
                            'is_terms_of_service':fields[16],
                            'is_mobile_authentication':fields[17],
                            'is_dormant_account':fields[18],
                            'is_deleted':fields[19],
                            'is_site_register':fields[20],
                        }
                    )
                except:
                    messages.error(request, 'CSV data type is incorrect!')
            url = reverse('user_admin:index')
            return HttpResponseRedirect(url)

        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/import_csv_form.html", payload
        )

    def profile_thumbnail(self, obj):
        return mark_safe('<img src="{}"/>'.format(obj.photo_thumbnail.url))

    profile_thumbnail.short_description = 'profile_thumbnail'

    def set_delete(self, request, queryset):
        queryset.update(is_deleted=True)

    def set_activate(self, request, queryset):
        queryset.update(is_deleted=False)

    def set_dormant_account(self, request, queryset):
        queryset.update(is_dormant_account=True)

    def set_activated_account(self, request, queryset):
        queryset.update(is_dormant_account=False)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "nickname", "point", "email_notifications")
    list_display_links = ['id', 'user', 'nickname']
    list_per_page = 20


class SendingEmailMonitorAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SendingEmailMonitor._meta.get_fields()]
    list_display_links = ['id', 'vendor']
    list_per_page = 20


class PagesAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    list_display_links = ['id', 'title']
    list_per_page = 20

user_admin_site.register(User, CustomUserAdmin)
user_admin_site.register(UserProfile, UserProfileAdmin)
user_admin_site.register(SendingEmailMonitor, SendingEmailMonitorAdmin)
user_admin_site.register(PolicyPages, PagesAdmin)