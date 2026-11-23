import re

from django import template

from common.components.django_redis_cache_components import (
    MAIN_MENU_KEY,
    SITE_INFO_KEY,
    cached,
)
from home.models.default import MainMenu, SiteInfo

register = template.Library()

# menu_icon is admin input that lands in a class attribute: only a bare LineIcons class name passes
_ICON_RE = re.compile(r"lni-[a-z0-9-]+")
_APP_ICONS = {"home": "lni-home", "portfolio": "lni-briefcase", "blog": "lni-pencil-alt", "board": "lni-clipboard"}


# 무효화는 common/cache_invalidation.py가 저장·삭제·mptt 이동 뒤에 한다.
@register.simple_tag
def main_menu_tag():
    return cached(MAIN_MENU_KEY, lambda: list(MainMenu.objects.all()))


@register.simple_tag
def site_info_tag():
    return cached(SITE_INFO_KEY, SiteInfo.objects.first)


@register.filter
def menu_icon_class(node):
    """LineIcons class for a menu entry: its own menu_icon when valid, else one picked by the url's app."""
    icon = (node.menu_icon or "").strip()
    if _ICON_RE.fullmatch(icon):
        return icon
    return _APP_ICONS.get((node.menu_path or "").partition(":")[0], "lni-link")
