import secrets
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile, SellerProfile, PhoneVerificationOTP
from .validators import validate_tz_phone, normalize_tz_phone

UserModel = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "avatar", "bio", "region", "district", "ward",
            "street_address", "preferred_language", "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at"]


class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = [
            "business_name", "slug", "tagline", "description",
            "business_phone", "whatsapp_number", "region", "district",
            "ward", "street_address", "logo", "banner",
            "verification_status", "national_id_number", "rating",
            "reviews_count", "is_trusted", "created_at", "updated_at"
        ]
        read_only_fields = ["slug", "verification_status", "rating", "reviews_count", "is_trusted", "created_at", "updated_at"]


class UserMeSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    seller_profile = SellerProfileSerializer(required=False)

    class Meta:
        model = UserModel
        fields = [
            "id", "username", "email", "phone_number", "role",
            "is_phone_verified", "is_email_verified", "profile",
            "seller_profile", "created_at"
        ]
        read_only_fields = ["id", "is_phone_verified", "is_email_verified", "created_at"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)
        seller_data = validated_data.pop("seller_profile", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile if passed
        if profile_data:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
            instance.profile = profile

        # Update seller profile if passed
        if seller_data:
            seller, _ = SellerProfile.objects.get_or_create(
                user=instance,
                defaults={"business_name": f"Shop-{instance.username}"}
            )
            for attr, value in seller_data.items():
                setattr(seller, attr, value)
            seller.save()
            instance.seller_profile = seller

        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    phone_number = serializers.CharField(required=False, allow_blank=True, validators=[validate_tz_phone])

    class Meta:
        model = UserModel
        fields = ["username", "email", "phone_number", "password", "role"]

    def validate_email(self, value):
        norm = value.lower().strip()
        if UserModel.objects.filter(email=norm).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        return norm

    def validate_phone_number(self, value):
        if not value:
            return None
        norm = normalize_tz_phone(value)
        if UserModel.objects.filter(phone_number=norm).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return norm

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = UserModel(**validated_data)
        user.set_password(password)
        user.save()

        # Ensure user profile is created
        UserProfile.objects.get_or_create(user=user)

        # If role is seller, create base seller profile
        if user.role == UserModel.ROLE_SELLER:
            base_name = f"Shop {user.username}"
            SellerProfile.objects.get_or_create(
                user=user,
                defaults={"business_name": base_name, "business_phone": user.phone_number}
            )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        identifier = attrs.get("email") or attrs.get("phone_number") or attrs.get("username")
        password = attrs.get("password")

        if not identifier or not password:
            raise serializers.ValidationError("Must provide email/phone/username and password.")

        # Identify user
        user = None
        if "@" in identifier:
            user = UserModel.objects.filter(email__iexact=identifier).first()
        else:
            # Check phone number (normalized)
            normalized_phone = normalize_tz_phone(identifier)
            if normalized_phone:
                user = UserModel.objects.filter(phone_number=normalized_phone).first()
            if not user:
                user = UserModel.objects.filter(username=identifier).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials. Please verify your email/phone and password.")

        if not user.is_active:
            raise serializers.ValidationError("This account is currently inactive or suspended.")

        attrs["user"] = user
        return attrs


class VerifyPhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, validators=[validate_tz_phone])
    otp_code = serializers.CharField(required=True, max_length=6, min_length=4)

    def validate(self, attrs):
        phone = normalize_tz_phone(attrs["phone_number"])
        code = attrs["otp_code"].strip()

        otp_record = PhoneVerificationOTP.objects.filter(
            phone_number=phone,
            is_used=False
        ).order_by("-created_at").first()

        if not otp_record or not otp_record.is_valid(code):
            if otp_record:
                otp_record.attempts += 1
                otp_record.save(update_fields=["attempts"])
            raise serializers.ValidationError("Invalid or expired OTP verification code.")

        attrs["otp_record"] = otp_record
        attrs["normalized_phone"] = phone
        return attrs
