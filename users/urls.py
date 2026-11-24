from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    RequestPhoneOTPView,
    VerifyPhoneView,
    UserMeView,
    PasswordChangeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    # Auth endpoints
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/request-phone-otp/", RequestPhoneOTPView.as_view(), name="auth-request-phone-otp"),
    path("auth/verify-phone/", VerifyPhoneView.as_view(), name="auth-verify-phone"),
    path("auth/password/change/", PasswordChangeView.as_view(), name="auth-password-change"),
    path("auth/password/reset/", PasswordResetRequestView.as_view(), name="auth-password-reset"),
    path("auth/password/reset/confirm/", PasswordResetConfirmView.as_view(), name="auth-password-reset-confirm"),

    # User profile endpoints
    path("users/me/", UserMeView.as_view(), name="users-me"),
]
