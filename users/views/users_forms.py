from django import forms
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404

from ..models import User, UserProfile
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


class ProfileForm(forms.ModelForm):

    password = forms.CharField(label='Old Password',
                               min_length=6, max_length=20,
                               help_text=_('Enter old password'),widget=forms.PasswordInput(attrs={'placeholder': 'Enter old password'}), required=False)

    new_password = forms.CharField(label='New Password',
                               min_length=6, max_length=20,
                               help_text=_('Enter new password'),widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password'}), required=False)

    new_password_confirm = forms.CharField(label='Password confirm',
                               min_length=6, max_length=20,
                               widget=forms.PasswordInput,
                               help_text=_('Enter password confirm'), required=False)

    email_notifications = forms.BooleanField(label='Email notifications',
                               widget=forms.CheckboxInput, required=False)

    class Meta:
        model = User
        fields = [ "nickname", "first_name", "last_name","gender", "profile_image"]
        # fields = "__all__"
        labels = {
            "nickname": _("Nickname"),
            "first_name": _("First Name"),
            "last_name": _("Last Name"),
            "gender": _("Gender"),
            "profile_image": _("Profile Image"),
        }
        widgets = {}
        help_texts = {}
        error_messages = {}

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()

        password = self.cleaned_data.get("password")
        new_password = self.cleaned_data.get("new_password")
        new_password_confirm = self.cleaned_data.get("new_password_confirm")

        if password or new_password or new_password_confirm:
            if not password :
                self.add_error("password", "Old password is empty")
            if not new_password :
                self.add_error("new_password", "Password is empty")
            if not new_password_confirm :
                self.add_error("new_password_confirm", "New password confirm is empty")

            if not self.instance.check_password(password):
                self.add_error("password", "Old password is incorrect")

            if new_password != new_password_confirm:
                self.add_error("new_password_confirm", "Password doesn't match")

        return cleaned_data


    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(ProfileForm, self).save(commit=False)
        UserProfile.objects.filter(user=self.instance.pk).update(email_notifications=self.cleaned_data['email_notifications'])
        if self.cleaned_data['new_password']:
            user.set_password(self.cleaned_data["new_password"])
        if commit:
            user.save()
        return user