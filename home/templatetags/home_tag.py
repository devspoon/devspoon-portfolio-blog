from django import template

from common.components.django_redis_cache_components import (
    MAIN_MENU_KEY,
    SITE_INFO_KEY,
    cached,
)
from home.models.default import MainMenu, SiteInfo

register = template.Library()


# 무효화는 common/cache_invalidation.py가 저장·삭제·mptt 이동 뒤에 한다.
@register.simple_tag
def main_menu_tag():
    return cached(MAIN_MENU_KEY, lambda: list(MainMenu.objects.all()))


@register.simple_tag
def site_info_tag():
    return cached(SITE_INFO_KEY, SiteInfo.objects.first)
