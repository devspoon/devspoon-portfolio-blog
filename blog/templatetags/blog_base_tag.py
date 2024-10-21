import logging

from django import template
from django.conf import settings
from django.core.paginator import Page
import re
from django.utils.html import strip_tags

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))
register = template.Library()


@register.filter(name="main_menu")
def is_manager(user):
    if user.is_superuser:
        return True

    groups = user.groups.all().values_list("name", flat=True)
    return True if "manager" in groups else False


@register.filter(name="slice_visible_pages")
def slice_visible_pages(paging: Page):
    min_page = int((paging.number - 1) / 10) * 10 + 1
    min_page = max(min_page, 1)
    max_page = min(min_page + 9, paging.paginator.num_pages)
    return range(min_page, max_page + 1)


@register.filter(name="remove_styles")
def remove_styles(value):
    # 모든 인라인 스타일 속성 제거
    no_styles = re.sub(r'style="[^"]*"', "", value)
    return strip_tags(no_styles)  # 스타일 제거 후 모든 태그 제거
