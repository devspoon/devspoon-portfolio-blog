import factory
from faker import Faker

fake = Faker()

from django.contrib.auth.models import User

from blog.models.blog import ProjectPost
from blog.models.blog_reply import ProjectPostReply


class UserFactory(factory.django.DjangoModelFactory):
    pass
