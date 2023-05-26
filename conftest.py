import factory
import pytest
from pytest_factoryboy import register

from board.models.board import Notice
from users.models import User
from users.tests.factories import FakeUserFactory, StaticUserFactory

register(StaticUserFactory)
register(FakeUserFactory)


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
