import logging
from datetime import datetime, timedelta

from braces.views import AnonymousRequiredMixin
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, TemplateView, UpdateView, View

from utils.email.verify_email_mixins import VerifyEmailMixin

from ..models import (
    PolicyPages,
    SendingEmailMonitor,
    User,
    UserProfile,
    UserVerification,
    UserRegistHistory,
)
from .users_forms import (
    LoginForm,
    ProfileForm,
    RegisterForm,
    ResendVerificationEmailForm,
    ResetPasswordForm,
    UpdatePasswordForm,
    ReplacePasswordForm,
)

# Create your views here.
logger = logging.getLogger(getattr(settings, "USERS_LOGGER", "django"))


def update_or_create_sending_email_result(result: list) -> None:
    if not SendingEmailMonitor.objects.filter(
        vendor=settings.MAIL_VENDOR, this_month=timezone.now().month
    ).first():
        obj = SendingEmailMonitor.objects.create(
            vendor=settings.MAIL_VENDOR,
            this_month=timezone.now().month,
            last_sending_state=False,
        )
        logger.debug(
            f"SendingEmailMonitor create this month {timezone.now().month} : {obj}"
        )

    if result["sending_mail_num"] == 0:
        obj = SendingEmailMonitor.objects.filter(
            vendor=settings.MAIL_VENDOR, this_month=timezone.now().month
        ).update(
            sending_failed_cnt=F("sending_failed_cnt") + 1,
            sending_total_cnt=F("sending_total_cnt") + 1,
            last_sending_state=False,
            last_failed_at=timezone.now(),
        )
        logger.debug(f"SendingEmailMonitor sending fail {obj}")
    else:
        obj = SendingEmailMonitor.objects.filter(
            vendor=settings.MAIL_VENDOR, this_month=timezone.now().month
        ).update(
            sending_success_cnt=F("sending_success_cnt") + 1,
            sending_total_cnt=F("sending_total_cnt") + 1,
            last_sending_state=True,
            last_success_at=timezone.now(),
        )
        logger.debug(f"SendingEmailMonitor sending success {obj}")


class RegisterView(VerifyEmailMixin, FormView):
    template_name = "users/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("users:login")
    verify_email_template_name1 = "/email/registration_verification.html"
    verify_email_template_name2 = "/email/verification.html"
    token_gen_type = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["policy_pages"] = PolicyPages.objects.all()
        return context

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        username = form.cleaned_data["username"]
        nickname = form.cleaned_data["nickname"]
        profile_image = form.cleaned_data["profile_image"]

        if User.objects.filter(email=email).exists():
            messages.error(self.request, "This email is exist")
            return redirect(reverse("users:register"))

        if User.objects.filter(username=username).exists():
            messages.error(self.request, "This username is exist")
            return redirect(reverse("users:register"))

        if User.objects.filter(nickname=nickname).exists():
            messages.error(self.request, "This nickname is exist")
            return redirect(reverse("users:register"))

        if profile_image:
            user = User.objects.create_user(
                email=email,
                password=password,
                username=username,
                nickname=nickname,
                profile_image=profile_image,
                is_site_register=True,
            )
        else:
            user = User.objects.create_user(
                email=email,
                password=password,
                username=username,
                nickname=nickname,
                is_site_register=True,
            )

        result = self.send_verification_email_management(
            self.verify_email_template_name1,
            settings.DEFAULT_FROM_EMAIL,
            user,
            self.token_gen_type,
        )

        logger.info(
            "result of sending mail number  = {}, token = {}".format(
                result["sending_mail_num"], result["token"]
            )
        )

        update_or_create_sending_email_result(result)

        messages.success(
            self.request,
            "A confirmation email will be sent to your mailbox. The link included in this email is valid for 3 days. After that you will need to register again.",
        )

        if result["sending_mail_num"] == 0:
            UserVerification.objects.create(
                user=user, key=result["token"], sending_result=False, verify_name=0
            )
        else:
            expired_at = timezone.now() + timedelta(days=3)
            UserVerification.objects.create(
                user=user,
                key=result["token"],
                expired_at=expired_at,
                sending_result=True,
                verify_name=0,
            )

        ip_address = self.request.META.get("REMOTE_ADDR")
        UserRegistHistory.objects.create(
            email=email,
            username=username,
            nickname=nickname,
            ip_address=ip_address,
        )

        return super().form_valid(form)


class ResendVerificationEmailView(VerifyEmailMixin, FormView):
    template_name = "users/resend_email.html"
    success_url = reverse_lazy("home:index")
    form_class = ResendVerificationEmailForm
    success_url = reverse_lazy("users:login")
    verify_email_template_name1 = "/email/registration_verification.html"
    verify_email_template_name2 = "/email/verification.html"
    token_gen_type = 1

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = User.user_objects.get_users().get(email=email, is_site_register=True)

        result = self.send_verification_email_management(
            self.verify_email_template_name1,
            settings.DEFAULT_FROM_EMAIL,
            user,
            self.token_gen_type,
        )

        logger.info(
            "generator success sending mail number  = {}, token = {}".format(
                result["sending_mail_num"], result["token"]
            )
        )

        update_or_create_sending_email_result(result)

        if result["sending_mail_num"] == 0:
            UserVerification.objects.create(
                user=user, key=result["token"], sending_result=False, verify_name=0
            )
        else:
            expired_at = timezone.now() + timedelta(days=3)
            UserVerification.objects.create(
                user=user,
                key=result["token"],
                expired_at=expired_at,
                sending_result=True,
                verify_name=0,
            )

        return super().form_valid(form)


class LoginView(AnonymousRequiredMixin, FormView):
    template_name = "users/login.html"
    success_url = reverse_lazy("home:index")
    form_class = LoginForm

    # def get_context_data(self, **kwargs):
    #     logging.info(f"session info : {__class__.__name__} {self.request.user.is_authenticated} {timezone.now()} {self.request.session.get_expiry_date()}")
    #     return super().get_context_data(**kwargs)

    def form_valid(self, form):
        # logging.info(f"session info : {__class__.__name__} {self.request.user.is_authenticated} {timezone.now()} {self.request.session.get_expiry_date()}")
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        user_temp = User.user_objects.get_users().get(
            email=email, is_site_register=True
        )
        user = auth.authenticate(username=user_temp.username, password=password)
        if user:
            auth.login(self.request, user)
            # user= User.user_objects.get_users().get(username=user.username, is_site_register=True)
            self.request.session["email"] = user.email
            self.request.session["username"] = user.username
            user.last_login_ipaddress = self.request.META.get("REMOTE_ADDR")
            user.last_login_at = timezone.now()
            user.save()

            # password replacement check
            current_date = timezone.now()
            six_months_ago = (
                current_date - timedelta(days=settings.PASSWORD_REPLACEMENT_CYCLE * 30)
            ).replace(tzinfo=None)
            time_at = user.password_replacement_at.replace(tzinfo=None)
            datetime_format = "%Y-%m-%d %H:%M:%S.%f"
            datetime_result = datetime.strptime(str(time_at), datetime_format)

            if datetime_result < six_months_ago:
                self.success_url = "users/password_replacement.html"

            return super().form_valid(form)
        else:
            messages.warning(self.request, "Please check your email or password.")
            return redirect(reverse("users:login"))


class LogoutView(View):
    def get(self, request):
        auth.logout(request)
        return redirect(reverse("home:index"))


class UserDeleteView(View):
    def get(self, request, *args, **kwargs):
        User.objects.get(id=request.user.pk).set_delete()
        return redirect(reverse("users:login"))


class VerificationView(View):
    def get(self, request):
        key = request.GET.get("key", "")
        try:
            verification = UserVerification.objects.get(key=key)
            logger.info("VerificationView key :", extra={key})
        except UserVerification.DoesNotExist:
            messages.warning(
                self.request,
                "There is an error in the authentication key. please try again.",
            )
            return redirect(reverse("users:login"))

        if verification.verified is True:
            messages.warning(
                self.request, "Already this link was used for update password."
            )
            return redirect(reverse("users:login"))

        current = timezone.now()

        if verification.expired_at > current:
            verification.verified = True
            verification.verified_at = current
            verification.save()

            messages.success(self.request, "Authentication is complete.")

            if verification.verify_name == 0:
                user = verification.user
                user.verified = True
                user.save()

                return redirect(reverse("users:login"))

            if verification.verify_name == 1:
                return redirect("users:update_password", verification.user.id)

        else:
            messages.warning(
                self.request,
                "The certification validity period has expired. please try again.",
            )
            return redirect(reverse("users:resend_verification_email"))


class ForgetPasswordView(VerifyEmailMixin, FormView):
    template_name = "users/reset_password.html"
    form_class = ResetPasswordForm
    success_url = reverse_lazy("users:login")
    reset_password_template_name = "/email/reset_password_email.html"

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = User.user_objects.get_users().get(email=email, is_site_register=True)

        result = self.reset_password_management(
            self.reset_password_template_name, settings.DEFAULT_FROM_EMAIL, user
        )

        logger.info(
            "generator success sending mail number  = {}, token = {}".format(
                result["sending_mail_num"], result["token"]
            )
        )

        update_or_create_sending_email_result(result)

        if result["sending_mail_num"] == 0:
            UserVerification.objects.create(
                user=user, key=result["token"], sending_result=False, verify_name=1
            )
        else:
            expired_at = timezone.now() + timedelta(days=3)
            UserVerification.objects.create(
                user=user,
                key=result["token"],
                expired_at=expired_at,
                sending_result=True,
                verify_name=1,
            )

        return super().form_valid(form)


class UpdatePasswordView(FormView):
    template_name = "users/update_password.html"
    form_class = UpdatePasswordForm
    success_url = reverse_lazy("users:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["userid"] = self.kwargs.get("userid")
        return context

    def form_valid(self, form, **kwargs):
        password = form.cleaned_data["new_password"]
        users = User.user_objects.get_users().get(id=self.kwargs.get("userid"))

        users.password = make_password(password)
        users.save()

        return super().form_valid(form)


class PeriodicPasswordReplacementView(LoginRequiredMixin, FormView):
    template_name = "users/password_replacement.html"
    form_class = ReplacePasswordForm
    success_url = reverse_lazy("home:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["userid"] = self.kwargs.get("userid")
        return context

    def form_valid(self, form, **kwargs):
        old_password = form.cleaned_data["old_password"]
        new_password = form.cleaned_data["new_password"]

        if check_password(old_password, self.request.user.password):
            self.request.user.set_password(new_password)
            self.request.user.save()
        else:
            messages.warning(self.request, "Old password is incorrect")
            return redirect(
                reverse("users:replace_password", args=[self.request.user.id])
            )

        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = "users/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        # logging.info(f"session info : {__class__.__name__} {self.request.user.is_authenticated} {timezone.now()} {self.request.session.get_expiry_date()}")
        context = super().get_context_data()
        userprofile = UserProfile.objects.filter(user_id=self.request.user.pk).first()
        context["user_point"] = userprofile.point
        context["email_notifications"] = userprofile.email_notifications
        return context

    # def form_valid(self, form, **kwargs):
    #     return super().form_valid(form)

    # def form_invalid(self, form, **kwargs):
    # # error status test code

    #     for field in form :
    #         if field.errors:
    #             for error in field.errors:
    #                 print(f"{field} is {error}error!!! ")

    #     return super().form_invalid(form)
