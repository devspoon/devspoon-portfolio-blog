from django.urls import path, include
from . import views

from .views.users import RegisterView, VerificationView, LoginView, LogoutView, ForgetPasswordView, ResendVerificationEmailView, UpdatePasswordView

app_name = "users"

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/email/resend', ResendVerificationEmailView.as_view(), name='resend_verification_email'),
    path('verify/', VerificationView.as_view(), name='verification_email'),
    path('password/send/', ForgetPasswordView.as_view(), name='forget_password'),
    path('password/update/<int:userid>/', UpdatePasswordView.as_view(), name='update_password'),
]