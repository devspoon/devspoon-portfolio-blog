from django.utils.html import strip_tags
from django.template.response import TemplateResponse


class TrimHtmlTagsAdminMixin:
    def get_cleaned_title(self, obj):
        # HTML 태그를 제거하고 텍스트만 반환한다. 인자 없는 format_html은 문자열을
        # 이스케이프 없이 안전 표시해 저장된 XSS가 되고, Django 6.0에서 제거된다.
        return strip_tags(obj.title)

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
                    response.context_data["subtitle"] = strip_tags(
                        response.context_data["subtitle"]
                    )

        return response