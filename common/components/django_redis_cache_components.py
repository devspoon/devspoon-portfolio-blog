import logging
from typing import Union

from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db.models import QuerySet

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)

REDIS_CONN = getattr(settings, "REDIS_CONNECTION")

logger = logging.getLogger(getattr(settings, "COMMON_LOGGER", "django"))

redis_mode = True

# django-redis cache set
def dredis_cache_set(prefix: str, pk: int, **kwargs: dict) -> None:
    # kwargs를 가독성 있게 출력
    kwargs_output = ", ".join([f"{key}: {value}" for key, value in kwargs.items()])
    logger.debug(f"kwargs : {{{kwargs_output}}}")

    if not redis_mode:
        logger.debug("Not redis mode")
        return

    # kwargs가 하나 이상의 키를 가지고 있고, 첫 번째 키의 값이 존재하는지 확인
    if kwargs and any(value is not None for value in kwargs.values()):
        for key, value in kwargs.items():
            redis_key = prefix + ":" + str(pk) + ":" + key
            logger.debug(f"redis key : {redis_key}")
            if hasattr(value, "__dict__"):
                logger.debug(f"redis value : {value.__dict__}")
            else:
                logger.debug(f"redis value : {value}")
            result = cache.set(redis_key, value, timeout=CACHE_TTL, nx=False)
            logger.debug(f"cache.set result : {result}")


# django-redis cache get
def dredis_cache_get(prefix: str, pk: int, key: str = None) -> Union[QuerySet, dict]:
    # logger.debug(f"key : {key}")
    key_value_dict = {}
    if key:
        redis_key = prefix + ":" + str(pk) + ":" + key
        logger.debug(f"redis key : {redis_key}")
        cache_result = cache.get(redis_key)
        logger.debug(f"redis result : {cache_result}")

        return cache_result
    else:
        redis_key = prefix + ":" + str(pk) + ":*"
        split_key = prefix + ":" + str(pk) + ":"
        logger.debug(f"redis key : {redis_key}")
        logger.debug(f"split key : {split_key}")
        for key in cache.iter_keys(redis_key):
            logger.debug(f"REDIS_CONN.scan_iter's key : {key}")
            keyword = key.replace(split_key, "", 1)
            if keyword == "get_queryset":
                continue
            key_value_dict[keyword] = cache.get(key)
            logger.debug(f"key_value_dict[{keyword}] : {key_value_dict[keyword]}")
        return key_value_dict


# django-redis cache set
def dredis_cache_delete(prefix: str, pk: int = None, key: str = None) -> None:
    logger.debug(f"key : {key}")

    if not redis_mode:
        logger.debug("Not redis mode")
        return

    if pk:
        if key:
            redis_key = prefix + ":" + str(pk) + ":" + key
        else:
            redis_key = prefix + ":" + str(pk) + ":*"
    else:
        redis_key = prefix + ":*"
    logger.debug(f"redis key : {redis_key}")
    cache.delete_pattern(redis_key, itersize=100_000)


def dredis_cache_check_key(prefix: str, pk: int, key: str) -> bool:
    # logger.debug(f"key : {key}")
    redis_key = prefix + ":" + str(pk) + ":" + key
    logger.debug(f"redis key : {redis_key}")
    if not redis_mode:
        logger.debug("Not redis mode")
        return False
    ttl = cache.ttl(redis_key)
    if ttl == 0:
        # the key is not exist or expired
        logger.debug("ttl == 0 : the key is not exist or expired")
        return False
    else:
        # If the key is less than 5 seconds, delete it and return false
        if ttl < 300:
            logger.debug(f"{ttl} : the key is less than 300 seconds")
            return False
        else:
            logger.debug(f"{ttl} : the key is over than 300 seconds")
            return True
