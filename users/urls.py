from django.urls import path

from .views.users import (
    ForgetPasswordView,
    LoginView,
    LogoutView,
    PrivacyPolicyView,
    ProfileView,
    RegisterView,
    ResendVerificationEmailView,
    TermsOfServiceView,
    UpdatePasswordView,
    UserDeleteView,
    VerificationView,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "verify/email/resend",
        ResendVerificationEmailView.as_view(),
        name="resend_verification_email",
    ),
    path("verify/", VerificationView.as_view(), name="verification_email"),
    path("password/send/", ForgetPasswordView.as_view(), name="forget_password"),
    path(
        "password/update/<int:userid>/",
        UpdatePasswordView.as_view(),
        name="update_password",
    ),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("delete/", UserDeleteView.as_view(), name="user_delete"),
    path("privacy-policy/", PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("terms-of-service", TermsOfServiceView.as_view(), name="terms_of_service"),
]
