from django import forms

from ..models import User
from django.utils.translation import gettext_lazy as _
from .validators import RegisteredEmailValidator, ResendVerificationEmailValidator, LoginVerificationEmailValidator, ResetPasswordEmailValidator

class RegisterForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}), validators=(forms.EmailField.default_validators + [RegisteredEmailValidator()]), help_text=_('Enter email address'), required=True)
    password = forms.CharField(label='Password',
                               min_length=8,
                               widget=forms.PasswordInput, help_text=_('Enter between 8'), required=True)
    password_confirm = forms.CharField(label='Password Confirm',
                                       min_length=8,
                                       widget=forms.PasswordInput, help_text=_('Enter the same password'), required=True)
    username = forms.CharField(label='User Name', min_length=4, max_length=20, help_text=_('Enter between 4 and 20 charactor'), required=True)

    nickname = forms.CharField(label='Nick Name', min_length=4, max_length=20, help_text=_('Enter between 4 and 20 charactor'), required=True)
    profile_image = forms.ImageField(label='Profile Image', required=False)

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError({
                    'password_confirm': ["Password information must be the same!"]
                })

        return cleaned_data


class ResendVerificationEmailForm(forms.Form):
     email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}), validators=(forms.EmailField.default_validators + [ResendVerificationEmailValidator()]), help_text=_('Enter email address'), required=True)


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}), validators=(forms.EmailField.default_validators + [LoginVerificationEmailValidator()]), help_text=_('Enter email address'), required=True)
    password = forms.CharField(label='Password',
                               min_length=6, max_length=20,
                               widget=forms.PasswordInput,
                               help_text=_('Enter password'), required=True)


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}), validators=(forms.EmailField.default_validators + [ResetPasswordEmailValidator()]), help_text=_('Enter email address'), required=True)


class UpdatePasswordForm(forms.Form):
    new_password = forms.CharField(label='Password',
                               min_length=6, max_length=20,
                               widget=forms.PasswordInput,
                               help_text=_('Enter password'), required=True)
    new_password_confirm = forms.CharField(label='Password confirm',
                               min_length=6, max_length=20,
                               widget=forms.PasswordInput,
                               help_text=_('Enter password'), required=True)

    def clean(self):
        cleaned_data = super(UpdatePasswordForm, self).clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')

        if new_password and new_password_confirm:
            if new_password != new_password_confirm:
                raise forms.ValidationError({
                    'new_password_confirm': ["Password information must be the same!"]
                })

        return cleaned_data
