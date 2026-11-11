import factory
import pytest
from django.core.cache import cache
from pytest_factoryboy import register

from board.models.board import Notice
from users.models import User
from users.tests.factories import FakeUserFactory, StaticUserFactory

register(StaticUserFactory)
register(FakeUserFactory)


@pytest.fixture(autouse=True)
def clear_redis_cache():
    """테스트 DB와 달리 redis 캐시는 실행 사이에 초기화되지 않는다.

    남은 키가 캐시 히트/미스 분기를 바꿔서 같은 테스트가 실행 순서와 이전
    실행 결과에 따라 다른 코드 경로를 타게 된다. 매 테스트 전후로 비운다.
    """
    cache.clear()
    yield
    cache.clear()


# help to use session scope with fixture of db and django_db
# @pytest.fixture(scope='session')
# def django_db_setup(django_db_setup, django_db_blocker):
#     pass


@pytest.fixture(scope="function")
def static_user(db, static_user_factory) -> object:
    # user = static_user_factory.build()
    user = static_user_factory.create()
    return user


@pytest.fixture(scope="function")
def user(client: object) -> object:
    # Create a user
    User.objects.create_user(
        username="testuser",
        password="password",
    )

    client.login(username="testuser", password="password")

    return client


@pytest.fixture(scope="function")
def staff(client: object) -> object:
    # Create a user
    User.objects.create_user(
        username="testuser",
        password="password",
        is_staff=True,
    )

    client.login(username="testuser", password="password")

    return client


class ContentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notice

    title = factory.Faker("sentence")
    content = factory.Faker("paragraph")


@pytest.fixture(scope="function")
def create_content(static_user) -> object:
    # Create a content fixture for app A that depends on the `create_user` fixture
    content = ContentFactory(author=static_user)
    return content
