import logging

from django import template
from django.conf import settings

from common.components.django_redis_cache_components import (
    dredis_cache_check_key,
    dredis_cache_delete,
    dredis_cache_get,
    dredis_cache_set,
)
from home.models.default import MainMenu, SiteInfo

logger = logging.getLogger(getattr(settings, "HOME_LOGGER", "django"))
register = template.Library()


@register.simple_tag
def main_menu_tag():
    cache_prefix = "home:main_menu"
    temp_pk = 0
    key = "main_menu"
    check_cached_key = dredis_cache_check_key(
        cache_prefix,
        temp_pk,
        key,
    )
    if check_cached_key:
        logger.debug(f"called redis cache - main_menu_tag")
        main_menu = dredis_cache_get(
            cache_prefix,
            temp_pk,
            key,
        )
    else:
        main_menu = MainMenu.objects.all()
        logger.debug("called database - main_menu_tag")
        if main_menu.exists():
            logger.debug("redis cache - main_menu_tag.exists")
            dredis_cache_set(
                cache_prefix,
                temp_pk,
                main_menu=main_menu,
            )
        else:
            logger.debug(f"redis cache - main_menu_tag not exists")

    return main_menu


@register.simple_tag
def site_info_tag():
    cache_prefix = "home:site_info"
    temp_pk = 0
    key = "site_info"
    check_cached_key = dredis_cache_check_key(
        cache_prefix,
        temp_pk,
        key,
    )
    if check_cached_key:
        logger.debug(f"called redis cache - site_info_tag")
        site_info = dredis_cache_get(
            cache_prefix,
            temp_pk,
            key,
        )
    else:
        site_info = SiteInfo.objects.first()
        logger.debug("called database - site_info_tag")
        if site_info is not None:
            logger.debug("redis cache - site_info_tag exists")
            dredis_cache_set(
                cache_prefix,
                temp_pk,
                site_info=site_info,
            )
        else:
            logger.debug(f"redis cache - site_info_tag not exists")

    return site_info
