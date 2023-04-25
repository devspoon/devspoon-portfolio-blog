import pytest
from pytest_factoryboy import register

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
