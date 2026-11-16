"""phase7 전환용 세션 엔진 (docs/crp/groups/phase7-session-store, ADR-007).

DB 세션 엔진과 같고, DB에서 세션을 못 찾았을 때만 옛 위치(Redis 캐시 세션)를 한 번 본다.
있으면 같은 세션 번호로 DB에 옮기고 그대로 로그인시킨다. 배포 뒤 move_sessions를 실행하기 전에
방문한 사용자도 로그아웃되지 않는다(못 찾으면 Django가 쿠키를 지운다).

shortcut: 전환 전용. move_sessions로 남은 세션까지 옮긴 뒤 다음 배포에서 SESSION_ENGINE을
"django.contrib.sessions.backends.db"로 되돌리고 이 파일을 지운다(deploy.md).
"""

from django.contrib.sessions.backends.base import CreateError
from django.contrib.sessions.backends.cache import KEY_PREFIX
from django.contrib.sessions.backends.db import SessionStore as DBStore
from django.core.cache import caches

LEGACY_CACHE_ALIAS = "default"  # phase7 이전 SESSION_CACHE_ALIAS


class SessionStore(DBStore):
    def load(self):
        key = self.session_key
        data = super().load()  # 못 찾으면 session_key를 비우고 {}를 돌려준다
        if data or not key:
            return data
        legacy = caches[LEGACY_CACHE_ALIAS]
        old = legacy.get(KEY_PREFIX + key)
        if old is None:
            return data
        self._session_key = key
        self._session_cache = old
        try:
            self.save(must_create=True)
        except CreateError:
            pass  # 같은 번호의 행이 이미 있다(동시 요청·만료 행). 요청 끝 저장이 내용을 맞춘다
        legacy.delete(KEY_PREFIX + key)
        return old
