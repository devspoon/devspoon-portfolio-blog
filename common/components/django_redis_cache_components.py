import uuid

from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from common.core.replica_router import read_primary

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


# --- v2 캐시 ---
# 읽기는 키 1개를 get 1회로 한다. 요청 경로에서 SCAN(iter_keys·delete_pattern)과 ttl을 쓰지 않는다.
# 옛 키(prefix:pk:key)는 지우지 않고 TTL로 사라지게 둔다. 세션이 같은 DB라 clear()는 쓰지 않는다.

NAMESPACE = "v2"
INDEX_KEY = f"{NAMESPACE}:index"
MAIN_MENU_KEY = f"{NAMESPACE}:home:main_menu"
SITE_INFO_KEY = f"{NAMESPACE}:home:site_info"


def portfolio_key(lang_index) -> str:
    return f"{NAMESPACE}:portfolio:{lang_index}"


def all_portfolio_keys() -> list:
    # portfolio 모델의 language 값은 settings.LANGUAGES의 순번("0", "1", ...)이다.
    return [portfolio_key(index) for index in range(len(settings.LANGUAGES))]


def cached(key: str, build):
    """key를 읽고, 없으면 build() 결과를 저장해 돌려준다. None은 저장하지 않는다."""
    value = cache.get(key)
    if value is None:
        # 무효화 직후 늦은 replica에서 채우면 옛 값이 TTL 동안 남는다. 채울 때는 primary에서 읽는다.
        with read_primary():
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
