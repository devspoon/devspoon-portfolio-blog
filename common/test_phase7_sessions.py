"""phase7: 세션은 DB(django_session)에 저장한다."""

from datetime import timedelta

import pytest
from django.contrib.sessions.backends.cache import KEY_PREFIX as CACHE_SESSION_PREFIX
from django.contrib.sessions.backends.cache import SessionStore as CacheSessionStore
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.management import call_command
from django.db import router
from django.test import Client
from django.utils import timezone

from common.core.replica_router import ReplicationRouter
from users.models import User
from users.tasks import clear_expired_sessions

headers = {"HTTP_USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/112.0"}


@pytest.fixture
def user():
    return User.objects.create_user(username="u", email="u@example.com", nickname="u", password="password")


def logged_in(client):
    return client.get("/").wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_login_session_is_a_db_row_and_survives_a_cache_flush(user):
    c = Client(**headers)
    c.force_login(user)
    assert Session.objects.filter(session_key=c.session.session_key).exists()
    cache.clear()  # Redis를 비워도(재시작·축출·운영 조치) 로그인은 유지된다
    assert logged_in(c)


@pytest.mark.django_db(databases=["default", "replica1"])
def test_session_is_read_from_the_primary_even_if_the_replica_lags(user, monkeypatch):
    User.objects.using("replica1").bulk_create([user])  # 사용자는 오래전에 복제돼 있다(시그널 없이 복사)
    c = Client(**headers)
    c.force_login(user)  # 방금 만든 세션 행은 default에만 있다(아직 복제 전)
    monkeypatch.setattr(router, "routers", [ReplicationRouter()])
    assert logged_in(c)


@pytest.mark.django_db
def test_session_lifetime_is_two_weeks_from_the_last_request(user):
    c = Client(**headers)
    c.force_login(user)
    logged_in(c)
    expire = Session.objects.get(session_key=c.session.session_key).expire_date
    assert abs(expire - (timezone.now() + timedelta(days=14))) < timedelta(minutes=1)


def _redis_session(user):
    s = CacheSessionStore()
    s["_auth_user_id"] = str(user.pk)
    s["_auth_user_backend"] = "django.contrib.auth.backends.ModelBackend"
    s["_auth_user_hash"] = user.get_session_auth_hash()
    s.create()
    return s.session_key


@pytest.mark.django_db
def test_move_sessions_keeps_users_logged_in(user):
    key = _redis_session(user)
    cache.set("phase7:unrelated", 1)

    call_command("move_sessions", "--dry-run")
    assert not Session.objects.filter(session_key=key).exists()
    assert cache.get(CACHE_SESSION_PREFIX + key) is not None

    call_command("move_sessions")
    assert Session.objects.filter(session_key=key).exists()
    assert cache.get(CACHE_SESSION_PREFIX + key) is None
    assert cache.get("phase7:unrelated") == 1  # 세션이 아닌 캐시 키는 건드리지 않는다

    call_command("move_sessions")  # 다시 실행해도 안전
    assert Session.objects.filter(session_key=key).count() == 1

    c = Client(**headers)
    c.cookies["sessionid"] = key
    assert logged_in(c)


@pytest.mark.django_db
def test_clear_expired_sessions_removes_only_expired_rows():
    now = timezone.now()
    Session.objects.create(session_key="expired", session_data="", expire_date=now - timedelta(seconds=1))
    Session.objects.create(session_key="valid", session_data="", expire_date=now + timedelta(days=1))
    clear_expired_sessions()
    assert list(Session.objects.values_list("session_key", flat=True)) == ["valid"]
