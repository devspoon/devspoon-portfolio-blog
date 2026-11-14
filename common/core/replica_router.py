import logging
from contextlib import contextmanager
from contextvars import ContextVar

from django.conf import settings

logger = logging.getLogger(getattr(settings, "COMMON_LOGGER", "django"))

# True인 동안 읽기를 default(primary)에서 한다. 쓰기 직후의 읽기가 늦은 replica의 옛 값을 보지 않게 한다(phase5 ADR-001).
_read_primary = ContextVar("read_primary", default=False)


@contextmanager
def read_primary():
    token = _read_primary.set(True)
    try:
        yield
    finally:
        _read_primary.reset(token)


class PrimaryForWritesMiddleware:
    """상태 변경 요청(POST 등)은 요청 안의 모든 읽기를 primary에서 한다. GET은 그대로 replica."""

    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in self.SAFE_METHODS:
            return self.get_response(request)
        with read_primary():
            return self.get_response(request)


class ReplicationRouter:
    def db_for_read(self, model, **hints):
        """
        Randomly pick a database to read from

        Note: If you have more than one replica, your db_for_read() method should instead randomly choose a replica, as the example in the Django docs does: return random.choice(['replica1', 'replica2']).
        """
        # return random.choice([key for key in settings.DATABASES]) # for All database
        # return random.choice(['replica1', 'replica2']) # for replica database
        # 세션은 로그인(POST, default에 저장) 직후 GET에서 바로 읽힌다. 늦은 replica에서 읽으면 로그아웃처럼 보인다(phase7 ADR-002).
        if _read_primary.get() or model._meta.app_label == "sessions":
            return "default"
        return "replica1"

    def db_for_write(self, model, **hints):
        """
        Always send write queries to the master database.
        """
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """
        This isn't really applicable for this use-case.
        """
        return True

        """
        Relations between objects are allowed if both objects are
        in the primary/replica pool.

        db_set = {'default', 'replica'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None
        """

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Only allow migration operations on the master database, just in case.
        """
        if db == "default":
            return True
        return None
