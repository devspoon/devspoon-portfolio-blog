import logging

from django.conf import settings

from common.components.django_redis_cache_components import dredis_cache_delete

logger = logging.getLogger(getattr(settings, "COMMON_LOGGER", "django"))


def index_cache_clean(original_function):
    def wrapper_function(*args, **kwargs):
        cache_prefix = "index"
        dredis_cache_delete(cache_prefix, 0)
        return original_function(*args, **kwargs)

    return wrapper_function
