"""Redis(캐시) 세션을 DB(django_session)로 옮긴다. phase7 배포 직후 한 번 실행한다.

옮긴 세션은 같은 세션 키를 쓰므로 사용자는 로그인된 그대로다. 다시 실행해도 안전하다.
일반 캐시 키는 건드리지 않는다. 키를 훑는 SCAN은 이 명령에서만 쓴다(요청 경로가 아님).
"""

from django.contrib.sessions.backends.cache import KEY_PREFIX
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core.cache import caches
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Move cache-backed sessions into the database session table."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Count only; change nothing.")
        parser.add_argument("--cache", default="default", help="Cache alias that held the sessions.")

    def handle(self, *args, dry_run=False, cache="default", **options):
        source = caches[cache]
        moved = skipped = 0
        for cache_key in source.iter_keys(f"{KEY_PREFIX}*"):
            session_key = cache_key[len(KEY_PREFIX):]
            data = source.get(cache_key)
            if dry_run:
                moved += data is not None
                continue
            if data is not None and not Session.objects.filter(session_key=session_key).exists():
                store = SessionStore(session_key=session_key)
                store._session_cache = data
                store.save(must_create=True)
                moved += 1
            else:
                skipped += 1
            source.delete(cache_key)
        verb = "would move" if dry_run else "moved"
        self.stdout.write(f"{verb} {moved} session(s), skipped {skipped}")
