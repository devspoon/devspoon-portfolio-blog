import logging
from typing import List, Union

from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db.models import QuerySet

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)

REDIS_CONN = getattr(settings, "REDIS_CONNECTION")

logger = logging.getLogger(getattr(settings, "COMMON_LOGGER", "django"))


# django-redis cache set
def dredis_cache_set(prefix: str, id: int, **kwargs: dict) -> None:
    logger.debug(f"kwargs : {kwargs}")
    for key, value in kwargs.items():
        redis_key = prefix + ":" + str(id) + ":" + key
        logger.debug(f"redis key : {redis_key}")
        cache.set(redis_key, value, timeout=CACHE_TTL, nx=True)


# django-redis cache get
def dredis_cache_get(prefix: str, id: int, key: str = None) -> Union[QuerySet, dict]:
    logger.debug(f"key : {key}")
    key_value_dict = {}
    if key:
        redis_key = prefix + ":" + str(id) + ":" + key
        logger.debug(f"redis key : {redis_key}")
        return cache.get(redis_key)
    else:
        redis_key = prefix + ":" + str(id) + ":*"
        split_key = prefix + ":" + str(id) + ":"
        logger.debug(f"redis key : {redis_key}")
        for key in cache.iter_keys(redis_key):
            logger.debug(f"REDIS_CONN.scan_iter's key : {key}")
            if key.strip(split_key) == "get_queryset":
                continue
            print("key.strip(split_key) : ", key.strip(split_key))
            key_value_dict[key.replace(split_key, "")] = cache.get(key)
        return key_value_dict


# django-redis cache set
def dredis_cache_delete(prefix: str, id: int, key: str = None) -> None:
    logger.debug(f"key : {key}")
    if key:
        redis_key = prefix + ":" + str(id) + ":" + key
        logger.debug(f"redis key : {redis_key}")
    else:
        redis_key = prefix + ":" + str(id) + ":*"
        logger.debug(f"redis key : {redis_key}")
    cache.delete_pattern(redis_key, itersize=100_000)


def dredis_cache_check_key(prefix: str, id: int, key: str) -> bool:
    logger.debug(f"key : {key}")
    redis_key = prefix + ":" + str(id) + ":" + key
    logger.debug(f"redis key : {redis_key}")
    ttl = cache.ttl(redis_key)
    if ttl == 0:
        # the key is not exist or expired
        logger.debug("ttl == 0 : the key is not exist or expired")
        return False
    else:
        # If the key is less than 5 seconds, delete it and return false
        if ttl < 5:
            logger.debug(f"{ttl} : the key is less than 5 seconds")
            return False
        else:
            logger.debug(f"{ttl} : the key is over than 5 seconds")
            return True
