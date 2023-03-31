import logging

from django import forms
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from ..models import User

logger = logging.getLogger(getattr(settings, "USERS_LOGGER", "django"))


class CustomUserCreationForm(UserCreationForm):
    password2 = forms.CharField(
        label=_("비밀번호 확인"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("비밀번호를 한 번 더 입력하세요."),
    )

    class Meta:
        model = User
        fields = "__all__"


class CustomUserChangeForm(UserChangeForm):
    password1 = forms.CharField(
        label=_("비밀번호"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
        required=False,
    )
    password2 = forms.CharField(
        label=_("비밀번호 확인"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("비밀번호를 한 번 더 입력하세요."),
        required=False,
    )

    class Meta:
        model = User
        fields = "__all__"
