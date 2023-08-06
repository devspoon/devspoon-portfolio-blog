from django.urls import path

from .views.users import (
    ForgetPasswordView,
    LoginView,
    LogoutView,
    ProfileView,
    RegisterView,
    ResendVerificationEmailView,
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
]
