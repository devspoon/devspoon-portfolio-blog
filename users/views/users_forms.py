import logging

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox, ReCaptchaV2Invisible, ReCaptchaV3
from email_validator import validate_email, EmailNotValidError, caching_resolver
from ..models import User, UserProfile
from .validators import (
    LoginVerificationEmailValidator,
    RegisteredEmailValidator,
    ResendVerificationEmailValidator,
    ResetPasswordEmailValidator,
)

logger = logging.getLogger(getattr(settings, "USERS_LOGGER", "django"))

resolver = caching_resolver(timeout=10)


class RegisterForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True}),
        validators=(forms.EmailField.default_validators + [RegisteredEmailValidator()]),
        help_text=_("Enter email address"),
        required=True,
    )
    password = forms.CharField(
        label="Password",
        min_length=8,
        widget=forms.PasswordInput,
        help_text=_("Enter between 8"),
        required=True,
    )
    password_confirm = forms.CharField(
        label="Password Confirm",
        min_length=8,
        widget=forms.PasswordInput,
        help_text=_("Enter the same password"),
        required=True,
    )
    username = forms.CharField(
        label="User Name",
        min_length=4,
        max_length=20,
        help_text=_("Enter between 4 and 20 character"),
        required=True,
    )

    nickname = forms.CharField(
        label="Nick Name",
        min_length=4,
        max_length=20,
        help_text=_("Enter between 4 and 20 character"),
        required=True,
    )

    profile_image = forms.ImageField(label="Profile Image", required=False)

    is_privacy_policy = forms.BooleanField(
        label="Privacy Policy (Click on the text below)",
        help_text=_("To sign up, you must read and agree to the linked policy."),
        required=True,
    )

    is_terms_of_service = forms.BooleanField(
        label="Terms of Service (Click on the text below)",
        help_text=_("To sign up, you must read and agree to the linked policy."),
        required=True,
    )

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def check_email_validation_with_dns(self, email: str) -> [str, bool]:
        try:
            if email is None:
                raise ValueError("Email is None type")
            logger.debug(
                "check_email_validation_with_dns email :", extra={"email": email}
            )
            emailinfo = validate_email(
                email, check_deliverability=True, dns_resolver=resolver
            )
            logger.debug(
                "emailinfo.normalized :", extra={"normalized": emailinfo.normalized}
            )
            return emailinfo.normalized, True

        except (EmailNotValidError, ValueError) as e:
            logger.debug(
                "Error :",
                extra={"error : ": str(e)},
            )
            return "", False

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        _, rt = self.check_email_validation_with_dns(email)
        if not rt:
            logger.debug(
                "The email failed validation. Please enter the email address you actually use",
                extra={"email : ": email},
            )
            raise forms.ValidationError(
                {
                    "email": [
                        "The email failed validation. Please enter the email address you actually use"
                    ]
                }
            )

        if password and password_confirm:
            if password != password_confirm:
                logger.debug(
                    "Password information must be the same :",
                    extra={"email : ": email},
                )
                raise forms.ValidationError(
                    message={
                        "password_confirm": ["Password information must be the same!"]
                    }
                )

        return cleaned_data


class ResendVerificationEmailForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True}),
        validators=(
            forms.EmailField.default_validators + [ResendVerificationEmailValidator()]
        ),
        help_text=_("Enter email address"),
        required=True,
    )


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True}),
        validators=(
            forms.EmailField.default_validators + [LoginVerificationEmailValidator()]
        ),
        help_text=_("Enter email address"),
        required=True,
    )
    password = forms.CharField(
        label="Password",
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput,
        help_text=_("Enter password"),
        required=True,
    )

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if not email:
            raise forms.ValidationError({"email": ["email must not be null or empty"]})

        if not password:
            raise forms.ValidationError(
                {"password": ["Password must not be null or empty"]}
            )

        return cleaned_data


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True}),
        validators=(
            forms.EmailField.default_validators + [ResetPasswordEmailValidator()]
        ),
        help_text=_("Enter email address"),
        required=True,
    )


class UpdatePasswordForm(forms.Form):
    new_password = forms.CharField(
        label="Password",
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput,
        help_text=_("Enter password"),
        required=True,
    )
    new_password_confirm = forms.CharField(
        label="Password confirm",
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput,
        help_text=_("Enter password"),
        required=True,
    )

    def clean(self):
        cleaned_data = super(UpdatePasswordForm, self).clean()
        new_password = cleaned_data.get("new_password")
        new_password_confirm = cleaned_data.get("new_password_confirm")

        if new_password and new_password_confirm:
            if new_password != new_password_confirm:
                raise forms.ValidationError(
                    {"new_password_confirm": ["Password information must be the same!"]}
                )

        return cleaned_data


class ReplacePasswordForm(forms.Form):
    old_password = forms.CharField(
        label="Old Password",
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput,
        help_text=_("Enter old password"),
        required=True,
    )
    new_password = forms.CharField(
        label="Password",
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput,
        help_text=_("Enter new password"),
        required=True,
    )
    new_password_confirm = forms.CharField(
        label="Password confirm",
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput,
        help_text=_("Enter password same like new password"),
        required=True,
    )

    def clean(self):
        cleaned_data = super(ReplacePasswordForm, self).clean()
        new_password = cleaned_data.get("new_password")
        new_password_confirm = cleaned_data.get("new_password_confirm")

        if new_password and new_password_confirm:
            if new_password != new_password_confirm:
                raise forms.ValidationError(
                    {"new_password_confirm": ["Password information must be the same!"]}
                )

        return cleaned_data


class ProfileForm(forms.ModelForm):
    password = forms.CharField(
        label="Old Password",
        min_length=8,
        max_length=20,
        help_text=_("Enter old password"),
        widget=forms.PasswordInput(attrs={"placeholder": "Enter old password"}),
        required=False,
    )

    new_password = forms.CharField(
        label="New Password",
        min_length=8,
        max_length=20,
        help_text=_("Enter new password"),
        widget=forms.PasswordInput(attrs={"placeholder": "Enter new password"}),
        required=False,
    )

    new_password_confirm = forms.CharField(
        label="Password confirm",
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput,
        help_text=_("Enter password confirm"),
        required=False,
    )

    email_notifications = forms.BooleanField(
        label="Email notifications", widget=forms.CheckboxInput, required=False
    )

    class Meta:
        model = User
        fields = [
            "notification_email",
            "nickname",
            "username",
            "gender",
            "profile_image",
        ]
        # fields = "__all__"
        labels = {
            "notification_email": _("Notification Email"),
            "nickname": _("Nickname"),
            "username": _("User Name"),
            "gender": _("Gender"),
            "profile_image": _("Profile Image"),
        }
        widgets = {}
        help_texts = {
            "notification_email": _(
                "Please fill out this field to receive notification emails."
            ),
            "nickname": _("Nicknames must be unique."),
        }
        error_messages = {}

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()

        password = self.cleaned_data.get("password")
        new_password = self.cleaned_data.get("new_password")
        new_password_confirm = self.cleaned_data.get("new_password_confirm")

        if password or new_password or new_password_confirm:
            if not password:
                self.add_error("password", "Old password is empty")
            if not new_password:
                self.add_error("new_password", "Password is empty")
            if not new_password_confirm:
                self.add_error("new_password_confirm", "New password confirm is empty")
            if not self.instance.check_password(password):
                self.add_error("password", "Old password is incorrect")
            if new_password != new_password_confirm:
                self.add_error("new_password_confirm", "Password doesn't match")

        return cleaned_data

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(ProfileForm, self).save(commit=False)
        UserProfile.objects.filter(user=self.instance.pk).update(
            email_notifications=self.cleaned_data["email_notifications"]
        )
        if self.cleaned_data["new_password"]:
            user.set_password(self.cleaned_data["new_password"])
        if commit:
            user.save()
        return user
