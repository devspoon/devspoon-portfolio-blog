import logging

from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.decorators import method_decorator
from common.decorators.cache import index_cache_clean
from django.utils.safestring import mark_safe
from django_summernote.admin import SummernoteModelAdmin
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.db import transaction
from blog.models.blog import ProjectPost
from common.mixin.admin.redis_cache_handler import AdminCacheCleanMixin
from common.mixin.admin.actions import CustomActionsAdminMixin
from common.mixin.admin.trim_html_tags import TrimHtmlTagsAdminMixin
from portfolio.models import (
    AboutProjects,
    EducationStudy,
    InterestedIn,
    PersonalInfo,
    Portfolio,
    PortfolioSummary,
    WorkExperience,
)

logger = logging.getLogger(getattr(settings, "PORTFOLIO_LOGGER", "django"))


# Register your models here.
class PortfolioAdminSite(AdminSite):
    site_header = "Portfolio Admin"
    site_title = "Portfolio Admin Portal"
    index_title = "Welcome to Portfolio Admin Portal"


portfolio_admin_site = PortfolioAdminSite(name="portfolio_admin")


class ProfileSummaryInline(
    admin.TabularInline,
):
    model = PortfolioSummary

class CustomAdminMixin(CustomActionsAdminMixin, TrimHtmlTagsAdminMixin, AdminCacheCleanMixin, SummernoteModelAdmin):
    pass

class PortfolioAdmin(CustomAdminMixin):
    cache_prefix = "portfolio"
    use_pk = False

    list_display = [
        "id",
        "portfolio_image_1",
        "portfolio_image_2",
        "portfolio_image_3",
        "language",
        "created_at",
    ]
    list_display_links = ["id", "language", "created_at"]
    fieldsets = [
        (
            "File Upload",
            {
                "fields": [
                    "portfolio_cv_file",
                    "portfolio_image1",
                    "portfolio_image_1",
                    "portfolio_image2",
                    "portfolio_image_2",
                    "portfolio_image3",
                    "portfolio_image_3",
                ],
                "classes": ["collapse"],
            },
        ),
        ("detail information", {"fields": ["language", "summary"]}),
    ]
    readonly_fields = [
        "portfolio_image_1",
        "portfolio_image_2",
        "portfolio_image_3",
        "created_at",
    ]
    inlines = [ProfileSummaryInline]
    summernote_fields = ("summary",)
    actions = [
        "delete_all_cache",
        "delete_selected_items",
        "copy_selected_items",
    ]

    def portfolio_image_1(self, obj):
        return mark_safe(
            '<img src="{}" style="width:250px;height:150px;"/>'.format(
                obj.portfolio_image1.url
            )
        )

    def portfolio_image_2(self, obj):
        return mark_safe(
            '<img src="{}" style="width:250px;height:150px;"/>'.format(
                obj.portfolio_image2.url
            )
        )

    def portfolio_image_3(self, obj):
        return mark_safe(
            '<img src="{}" style="width:250px;height:150px;"/>'.format(
                obj.portfolio_image3.url
            )
        )

    portfolio_image_1.short_description = "portfolio_image_preview_1"
    portfolio_image_2.short_description = "portfolio_image_preview_2"
    portfolio_image_3.short_description = "portfolio_image_preview_3"


class PersonalInfoAdmin(CustomAdminMixin):
    cache_prefix = "portfolio"
    use_pk = False

    list_display = ["id", "name", "language", "created_at"]
    list_display_links = ["id", "name"]
    list_editable = ("language",)

    actions = [
        "delete_all_cache",
        "delete_selected_items",
        "copy_selected_items",
    ]


class ProfileSummaryAdmin(CustomAdminMixin):
    cache_prefix = "portfolio"
    use_pk = False

    list_display = ["id", "position", "sort_num", "language", "skill", "created_at"]
    list_display_links = ["id", "position", "skill"]
    list_editable = (
        "sort_num",
        "language",
    )
    summernote_fields = ("content",)

    actions = [
        "delete_all_cache",
        "delete_selected_items",
        "copy_selected_items",
    ]


class WorkExperienceAdmin(CustomAdminMixin):
    cache_prefix = "portfolio"
    use_pk = False

    list_display = [
        "id",
        "get_cleaned_title",
        "role",
        "color",
        "sort_num",
        "language",
        "project_start_date",
    ]
    list_display_links = ["id", "get_cleaned_title", "role"]
    list_editable = (
        "color",
        "sort_num",
        "language",
    )
    summernote_fields = (
        "title",
        "summary",
        "content",
    )

    actions = [
        "delete_all_cache",
        "delete_selected_items",
        "copy_selected_items",  # 새로운 복사 액션 추가
    ]


class EducationStudyAdmin(CustomAdminMixin):
    cache_prefix = "portfolio"
    use_pk = False

    list_display = ["id", "title", "sort_num", "language", "created_at"]
    list_display_links = ["id", "title", "created_at"]
    list_editable = (
        "sort_num",
        "language",
    )
    summernote_fields = ("content",)

    actions = [
        "delete_all_cache",
        "delete_selected_items",
        "copy_selected_items",
    ]


class InterestedInAdmin(CustomAdminMixin):
    cache_prefix = "portfolio"
    use_pk = False

    list_display = ["id", "title", "language", "created_at"]
    list_display_links = ["id", "title"]
    list_editable = ("language",)
    fieldsets = [
        ("language", {"fields": ("language",)}),
        (
            "icon",
            {
                "fields": ("icon",),
                "description": '<div class="help">icon searching : <a href="https://lineicons.com/icons/" target="_blank">lineicons.com</a></div>',
            },
        ),
        ("content", {"fields": ("title", "content")}),
    ]
    summernote_fields = (
        "title",
        "content",
    )

    actions = [
        "delete_all_cache",
        "delete_selected_items",
        "copy_selected_items",
    ]


class AboutProjectsAdmin(CustomAdminMixin):
    cache_prefix = "portfolio"
    use_pk = False

    list_display = [
        "id",
        "projectpost",
        "sort_num",
        "language",
        "created_at",
    ]  # [field.name for field in AboutProjects._meta.get_fields()]
    list_display_links = ["id", "projectpost"]
    list_editable = (
        "sort_num",
        "language",
    )
    raw_id_fields = ("projectpost",)
    date_hierarchy = "created_at"

    actions = [
        "delete_all_cache",
        "delete_selected_items",
        "copy_selected_items",
    ]


    @method_decorator(index_cache_clean)
    def delete_selected_items(self, request, queryset):
        super().delete_selected_items(request, queryset)

    @method_decorator(index_cache_clean)
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    @method_decorator(index_cache_clean)
    def delete_model(self, request, obj):
        super().delete_model(request, obj)


class ProjectPostHiddenAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):  # tric regist
        return {}


portfolio_admin_site.register(Portfolio, PortfolioAdmin)
portfolio_admin_site.register(PersonalInfo, PersonalInfoAdmin)
portfolio_admin_site.register(PortfolioSummary, ProfileSummaryAdmin)
portfolio_admin_site.register(WorkExperience, WorkExperienceAdmin)
portfolio_admin_site.register(EducationStudy, EducationStudyAdmin)
portfolio_admin_site.register(InterestedIn, InterestedInAdmin)
portfolio_admin_site.register(AboutProjects, AboutProjectsAdmin)
portfolio_admin_site.register(ProjectPost, ProjectPostHiddenAdmin)
