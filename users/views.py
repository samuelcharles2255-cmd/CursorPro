import secrets
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PhoneVerificationOTP, UserProfile, SellerProfile
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    VerifyPhoneSerializer,
    UserMeSerializer,
    UserProfileSerializer,
    SellerProfileSerializer,
)
from .validators import normalize_tz_phone, validate_tz_phone

UserModel = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)

        user_data = UserMeSerializer(user).data
        return Response({
            "message": "User registered successfully.",
            "tokens": tokens,
            "user": user_data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = get_tokens_for_user(user)

        user_data = UserMeSerializer(user).data
        return Response({
            "message": "Login successful.",
            "tokens": tokens,
            "user": user_data
        }, status=status.HTTP_200_OK)


class RequestPhoneOTPView(APIView):
    """Generates a 6-digit OTP code for Tanzanian phone verification"""
    permission_classes = [AllowAny]

    def post(self, request):
        raw_phone = request.data.get("phone_number")
        if not raw_phone:
            return Response({"error": "phone_number is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_tz_phone(raw_phone)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        phone = normalize_tz_phone(raw_phone)
        otp_code = f"{secrets.randbelow(900000) + 100000}"

        PhoneVerificationOTP.objects.create(
            phone_number=phone,
            otp_code=otp_code,
            expires_at=timezone.now() + timezone.timedelta(minutes=5)
        )

        # In production this triggers Africa's Talking / Twilio SMS gateway
        return Response({
            "message": f"Verification code sent to {phone}.",
            "phone_number": phone,
            "dev_otp": otp_code  # Exposed for testing/development environments
        }, status=status.HTTP_200_OK)


class VerifyPhoneView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_record = serializer.validated_data["otp_record"]
        phone = serializer.validated_data["normalized_phone"]

        otp_record.is_used = True
        otp_record.save(update_fields=["is_used"])

        # Mark user as phone verified if logged in or matching phone
        if request.user.is_authenticated:
            request.user.phone_number = phone
            request.user.is_phone_verified = True
            request.user.save(update_fields=["phone_number", "is_phone_verified"])
        else:
            UserModel.objects.filter(phone_number=phone).update(is_phone_verified=True)

        return Response({
            "message": "Phone number successfully verified.",
            "phone_number": phone,
            "is_phone_verified": True
        }, status=status.HTTP_200_OK)


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserMeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response(
                {"error": "Both old_password and new_password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.check_password(old_password):
            return Response(
                {"error": "Incorrect current password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(new_password, request.user)
        except Exception as e:
            msg = list(e.messages) if hasattr(e, "messages") else str(e)
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password)
        request.user.save(update_fields=["password"])
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("email") or request.data.get("phone_number")
        if not identifier:
            return Response({"error": "email or phone_number is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if "@" in identifier:
            user = UserModel.objects.filter(email__iexact=identifier.strip()).first()
        else:
            norm_phone = normalize_tz_phone(identifier)
            if norm_phone:
                user = UserModel.objects.filter(phone_number=norm_phone).first()

        reset_code = f"{secrets.randbelow(900000) + 100000}"
        if user and user.phone_number:
            PhoneVerificationOTP.objects.create(
                phone_number=user.phone_number,
                otp_code=reset_code,
                expires_at=timezone.now() + timezone.timedelta(minutes=15)
            )

        return Response({
            "message": "If an account matches those credentials, a password reset code has been issued.",
            "dev_reset_code": reset_code if settings.DEBUG else None
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("email") or request.data.get("phone_number")
        code = request.data.get("code") or request.data.get("otp_code")
        new_password = request.data.get("new_password")

        if not identifier or not code or not new_password:
            return Response(
                {"error": "identifier (email/phone), reset code, and new_password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = None
        if "@" in identifier:
            user = UserModel.objects.filter(email__iexact=identifier.strip()).first()
        else:
            norm = normalize_tz_phone(identifier)
            if norm:
                user = UserModel.objects.filter(phone_number=norm).first()

        if not user or not user.phone_number:
            return Response({"error": "Invalid reset request or user has no registered phone."}, status=status.HTTP_400_BAD_REQUEST)

        otp = PhoneVerificationOTP.objects.filter(
            phone_number=user.phone_number,
            is_used=False
        ).order_by("-created_at").first()

        if not otp or not otp.is_valid(code.strip()):
            return Response({"error": "Invalid or expired reset code."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password, user)
        except Exception as e:
            msg = list(e.messages) if hasattr(e, "messages") else str(e)
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        otp.is_used = True
        otp.save(update_fields=["is_used"])
        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response({"message": "Password has been reset successfully. You can now log in with your new password."}, status=status.HTTP_200_OK)
