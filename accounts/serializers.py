from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.jobs.models import Skill
from apps.jobs.serializers import SkillSerializer
from .models import EmployerProfile, Profile, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "role", "email_verified", "auth_provider"]
        read_only_fields = ["email", "role", "email_verified", "auth_provider"]


class RegisterSerializer(serializers.ModelSerializer):
    """
    POST here to sign up. `role` decides job_seeker vs employer at signup —
    this is the "flexible" part: same endpoint, different account type.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "email", "name", "password", "password2", "role"]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password2": "Passwords don't match."})
        password_validation.validate_password(data["password"])
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        # username is required internally by AbstractUser but unused for login —
        # set it to the email so it's guaranteed unique without extra logic
        user = User(username=validated_data["email"], **validated_data)
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user)
        if user.role == User.ROLE_EMPLOYER:
            EmployerProfile.objects.create(user=user)
        return user


class LoginSerializer(TokenObtainPairSerializer):
    """Logs in with email + password, returns access/refresh tokens + user info."""
    username_field = User.USERNAME_FIELD  # "email"

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class GoogleLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    # write skill IDs here, read full skill objects back via `skills` above
    skill_ids = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), many=True, write_only=True, source="skills", required=False
    )

    class Meta:
        model = Profile
        fields = [
            "user", "bio", "location", "phone", "resume_url", "avatar_url",
            "skills", "skill_ids", "updated_at",
        ]
        read_only_fields = ["updated_at"]

    def update(self, instance, validated_data):
        skills = validated_data.pop("skills", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if skills is not None:
            instance.skills.set(skills)  # this is the line that later powers job matching
        return instance


class EmployerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = ["company", "job_title", "is_verified"]
        read_only_fields = ["is_verified"]  # only staff verifies — never trust self-reported


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value