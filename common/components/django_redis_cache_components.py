import logging
import uuid
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


# --- v2 캐시 (docs/crp/groups/phase3-cache-redesign, ADR-001·002·004·007) ---
# 읽기는 키 1개를 get 1회로 한다. 요청 경로에서 SCAN(iter_keys·delete_pattern)과 ttl을 쓰지 않는다.
# 옛 키(prefix:pk:key)는 지우지 않고 TTL로 사라지게 둔다. 세션이 같은 DB라 clear()는 쓰지 않는다.

NAMESPACE = "v2"
INDEX_KEY = f"{NAMESPACE}:index"
MAIN_MENU_KEY = f"{NAMESPACE}:home:main_menu"
SITE_INFO_KEY = f"{NAMESPACE}:home:site_info"


def portfolio_key(lang_index) -> str:
    return f"{NAMESPACE}:portfolio:{lang_index}"


def work_experience_key(lang_index) -> str:
    return f"{NAMESPACE}:portfolio:work:{lang_index}"


def all_portfolio_keys() -> list:
    # portfolio 모델의 language 값은 settings.LANGUAGES의 순번("0", "1", ...)이다.
    return [
        key
        for index in range(len(settings.LANGUAGES))
        for key in (portfolio_key(index), work_experience_key(index))
    ]


def cached(key: str, build):
    """key를 읽고, 없으면 build() 결과를 저장해 돌려준다. None은 저장하지 않는다."""
    value = cache.get(key)
    if value is None:
        value = build()
        if value is not None:
            cache.set(key, value, timeout=CACHE_TTL)
    return value


def replies_prefix(post_model) -> str:
    return f"{NAMESPACE}:replies:{post_model._meta.label_lower}"


def _reply_version_key(post_model, post_pk) -> str:
    return f"{replies_prefix(post_model)}:{post_pk}:ver"


def reply_page_key(post_model, post_pk, page: int) -> str:
    """글의 댓글 목록 페이지 키. 글마다 버전 토큰을 두어 버전 삭제 한 번으로 모든 페이지를 무효화한다."""
    version_key = _reply_version_key(post_model, post_pk)
    version = cache.get(version_key)
    if version is None:
        version = uuid.uuid4().hex
        # 동시에 버전을 만든 다른 요청이 있으면 먼저 저장된 값을 쓴다.
        if not cache.add(version_key, version, timeout=CACHE_TTL):
            version = cache.get(version_key) or version
    return f"{replies_prefix(post_model)}:{post_pk}:{version}:{page}"


def invalidate_replies(post_model, post_pk) -> None:
    # 옛 버전의 페이지 키는 아무도 읽지 않고 TTL로 사라진다.
    cache.delete(_reply_version_key(post_model, post_pk))
