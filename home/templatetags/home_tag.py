import logging

from django import template
from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from home.models.default import MainMenu, SiteInfo

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)
logger = logging.getLogger(getattr(settings, "HOME_LOGGER", "django"))
register = template.Library()


@register.simple_tag
def main_menu_tag():
    if "home:main_menu" in cache:
        main_menu = cache.get("home:main_menu")
    else:
        main_menu = MainMenu.objects.all()
        cache.set("home:main_menu", main_menu, timeout=CACHE_TTL)
    return main_menu


@register.simple_tag
def site_info_tag():
    if "home:site_info" in cache:
        site_info = cache.get("home:site_info")
    else:
        site_info = SiteInfo.objects.first()
        cache.set("home:site_info", site_info, timeout=CACHE_TTL)
    return site_info
