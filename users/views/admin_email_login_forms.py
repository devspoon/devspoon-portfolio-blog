import logging

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from ..models import User

logger = logging.getLogger(getattr(settings, "USERS_LOGGER", "django"))


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("username", "email")
