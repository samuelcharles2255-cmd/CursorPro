from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import EmployerProfile, Profile
from .serializers import (
    ChangePasswordSerializer,
    EmployerProfileSerializer,
    GoogleLoginSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


def _tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class RegisterView(generics.CreateAPIView):
    """POST /auth/register/  {email, password, password2, name, role} -> tokens + user"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"user": UserSerializer(user).data, **_tokens_for(user)},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """POST /auth/login/  {email, password} -> {access, refresh, user}"""
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    """POST /auth/logout/  {refresh} -> blacklists that refresh token."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            RefreshToken(request.data["refresh"]).blacklist()
        except Exception:
            return Response({"detail": "Invalid or missing refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /auth/me/ -> the logged-in user's own account (not profile)."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH /auth/profile/ -> bio, resume, skills.
    This is the endpoint that feeds job matching: whatever skills land
    here get compared against Job.skills to surface relevant jobs.
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class EmployerProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /auth/employer-profile/ -> only usable by role=employer accounts."""
    serializer_class = EmployerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if not self.request.user.is_employer:
            raise PermissionDenied("This account is not an employer account.")
        profile, _ = EmployerProfile.objects.get_or_create(user=self.request.user)
        return profile


class ChangePasswordView(APIView):
    """POST /auth/change-password/  {old_password, new_password} -> requires being logged in."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": "Wrong password."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password updated."})


class PasswordResetRequestView(APIView):
    """
    POST /auth/password-reset/  {email} -> emails a reset link.
    Always returns the same response whether or not the email exists —
    never let this endpoint be used to check who has an account.
    """
    permission_classes = [permissions.AllowAny]
    GENERIC_RESPONSE = {"detail": "If that email exists, a reset link has been sent."}

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email__iexact=serializer.validated_data["email"])
        except User.DoesNotExist:
            return Response(self.GENERIC_RESPONSE)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_path = f"/reset-password/{uid}/{token}"  # your frontend builds the full URL around this
        send_mail(
            subject="Reset your password",
            message=f"Use this link to reset your password: {reset_path}",
            from_email=None,  # falls back to DEFAULT_FROM_EMAIL
            recipient_list=[user.email],
        )
        return Response(self.GENERIC_RESPONSE)


class PasswordResetConfirmView(APIView):
    """POST /auth/password-reset-confirm/  {uid, token, new_password}"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            uid = force_str(urlsafe_base64_decode(data["uid"]))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"detail": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, data["token"]):
            return Response({"detail": "Invalid or expired link."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(data["new_password"])
        user.save()
        return Response({"detail": "Password reset. Log in with your new password."})


class GoogleLoginView(APIView):
    """
    POST /auth/google/  {id_token}
    Not fully live yet — needs `pip install google-auth` and
    GOOGLE_CLIENT_ID set in settings.py. The structure is built now so the
    User model never needs to change when you switch it on.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            from google.auth.transport import requests as google_requests
            from google.oauth2 import id_token as google_id_token
        except ImportError:
            return Response(
                {"detail": "Google login isn't installed yet. Run: pip install google-auth"},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        try:
            idinfo = google_id_token.verify_oauth2_token(
                serializer.validated_data["id_token"],
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except ValueError:
            return Response({"detail": "Invalid Google token."}, status=status.HTTP_400_BAD_REQUEST)

        email = idinfo["email"]
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "name": idinfo.get("name", ""),
                "auth_provider": User.AUTH_GOOGLE,
                "google_id": idinfo["sub"],
                "email_verified": True,
            },
        )
        if created:
            Profile.objects.create(user=user)

        return Response({"user": UserSerializer(user).data, **_tokens_for(user)})