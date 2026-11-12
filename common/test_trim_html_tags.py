"""TrimHtmlTagsAdminMixin 회귀 테스트 (phase2-deps-upgrade F-001, ADR-004).

제목 HTML은 태그를 걷어낸 텍스트로 보여야 한다. 그대로 안전 표시하면 admin에서 저장된 XSS가 된다.
"""
from types import SimpleNamespace

from django.template.response import TemplateResponse
from django.test import RequestFactory

from common.mixin.admin.trim_html_tags import TrimHtmlTagsAdminMixin

TITLE = '<b>Hello</b><script>alert("x")</script>'


def test_cleaned_title_strips_tags():
    cleaned = TrimHtmlTagsAdminMixin().get_cleaned_title(SimpleNamespace(title=TITLE))

    assert cleaned == 'Helloalert("x")'
    assert "<" not in cleaned


class FakeBaseAdmin:
    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        return TemplateResponse(request, "unused.html", {"subtitle": TITLE})


class FakeAdmin(TrimHtmlTagsAdminMixin, FakeBaseAdmin):
    pass


def test_changeform_subtitle_strips_tags():
    request = RequestFactory().get("/")

    response = FakeAdmin().changeform_view(request, object_id="1")

    assert response.context_data["subtitle"] == 'Helloalert("x")'
