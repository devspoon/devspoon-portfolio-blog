import logging

from django import forms
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from ..models import User

logger = logging.getLogger(getattr(settings, "USERS_LOGGER", "django"))


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = "__all__"


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"
