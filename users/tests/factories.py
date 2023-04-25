import factory
from faker import Faker

from users.models import User

fake = Faker()


class StaticUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = "test"
    nickname = "test1"
    email = "test@test.com"
    password = "test1324"
    verified = True
    is_site_register = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(model_class)
        # The default would use ``manager.create(*args, **kwargs)``
        return manager.create_user(*args, **kwargs)


class FakeUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyFunction(fake.name)
    nickname = factory.LazyFunction(fake.user_name)
    email = factory.LazyFunction(fake.email)
    password = factory.LazyFunction(fake.password)
    verified = True
    is_site_register = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(model_class)
        # The default would use ``manager.create(*args, **kwargs)``
        return manager.create_user(*args, **kwargs)
