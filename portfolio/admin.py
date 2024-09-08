import logging

from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django_summernote.admin import SummernoteModelAdmin
from django.utils.html import format_html
from django.template.response import TemplateResponse
from blog.models.blog import ProjectPost
from common.components.admin.admin_components import AdminCacheClean
from common.decorators.cache import index_cache_clean
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


class PortfolioAdmin(AdminCacheClean, SummernoteModelAdmin):
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
    ]

    def get_actions(self, request):
        actions = super(PortfolioAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions

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


class PersonalInfoAdmin(AdminCacheClean, admin.ModelAdmin):
    cache_prefix = "portfolio"
    use_pk = False

    list_display = ["id", "name", "language", "created_at"]
    list_display_links = ["id", "name"]
    list_editable = ("language",)

    actions = [
        "delete_all_cache",
        "delete_selected_items",
    ]

    def get_actions(self, request):
        actions = super(PersonalInfoAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions


class ProfileSummaryAdmin(AdminCacheClean, SummernoteModelAdmin):
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
    ]

    def get_actions(self, request):
        actions = super(ProfileSummaryAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions


class WorkExperienceAdmin(AdminCacheClean, SummernoteModelAdmin):
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
    ]

    def get_actions(self, request):
        actions = super(WorkExperienceAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions

    def get_cleaned_title(self, obj):
        # HTML 태그를 제거하고 텍스트만 반환
        return format_html(
            obj.title
        )  # 또는 obj.title.strip()으로 HTML 제거 가능, 만약 HTML 태그를 제거하고 싶다면, strip_tags를 사용

    get_cleaned_title.short_description = "Title"  # Admin에서 표시될 제목

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        response = super().changeform_view(request, object_id, form_url, extra_context)

        # response가 HttpResponseRedirect가 아닐 때만 context_data에 접근
        if isinstance(response, TemplateResponse):
            if object_id is not None:
                # title에서 HTML 태그를 제거
                if (
                    "subtitle" in response.context_data
                    and response.context_data["subtitle"]
                ):
                    response.context_data["subtitle"] = format_html(
                        response.context_data["subtitle"]
                    )

        return response


class EducationStudyAdmin(AdminCacheClean, SummernoteModelAdmin):
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
    ]

    def get_actions(self, request):
        actions = super(EducationStudyAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions


class InterestedInAdmin(AdminCacheClean, SummernoteModelAdmin):
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
    ]

    def get_actions(self, request):
        actions = super(InterestedInAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions


class AboutProjectsAdmin(AdminCacheClean, admin.ModelAdmin):
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
    ]

    def get_actions(self, request):
        actions = super(AboutProjectsAdmin, self).get_actions(request)
        del actions["delete_selected"]
        return actions

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
