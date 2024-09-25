from django.utils.html import format_html
from django.template.response import TemplateResponse


class TrimHtmlTagsAdminMixin:
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