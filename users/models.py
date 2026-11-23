from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .validators import validate_tz_phone, normalize_tz_phone


class User(AbstractUser):
    """
    Custom user model built with first-class support for Tanzanian marketplace identity.
    Allows login and authentication via email or verified Tanzanian mobile number.
    """
    ROLE_BUYER = "buyer"
    ROLE_SELLER = "seller"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_BUYER, "Buyer / Mnunuzi"),
        (ROLE_SELLER, "Seller / Muuzaji"),
        (ROLE_ADMIN, "Admin / Msimamizi"),
    ]

    email = models.EmailField(_("email address"), unique=True, db_index=True)
    name = models.CharField(_("full name"), max_length=255, blank=True)
    phone_number = models.CharField(
        _("phone number"),
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_tz_phone],
        db_index=True,
        help_text=_("Tanzanian phone number (e.g. +255712345678 or 0712345678)")
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_BUYER)

    is_phone_verified = models.BooleanField(_("phone verified"), default=False)
    is_email_verified = models.BooleanField(_("email verified"), default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Disambiguate reverse accessors so User can coexist cleanly regardless of AUTH_USER_MODEL config
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="custom_user_groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_user_permissions",
        related_query_name="user",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users_custom"
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-created_at"]

    def __str__(self):
        return self.email or self.phone_number or self.username

    def clean(self):
        super().clean()
        if self.phone_number:
            self.phone_number = normalize_tz_phone(self.phone_number)
        if self.email:
            self.email = self.email.lower().strip()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_seller(self) -> bool:
        return self.role == self.ROLE_SELLER or hasattr(self, "seller_profile")

    @property
    def display_name(self) -> str:
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username or self.email


class UserProfile(models.Model):
    """
    Standard customer/buyer profile storing personal details and preferences.
    Decoupled from User model to keep auth light and queries performant.
    """
    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE,
        related_name="profile"
    )
    avatar = models.ImageField(upload_to="profiles/avatars/%Y/%m/", null=True, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    region = models.CharField(max_length=100, blank=True, db_index=True, help_text="e.g. Dar es Salaam, Mbeya, Arusha")
    district = models.CharField(max_length=100, blank=True, db_index=True, help_text="e.g. Kinondoni, Ilala, Temeke, Mbeya Mjini")
    ward = models.CharField(max_length=100, blank=True, help_text="e.g. Kariakoo, Sinza, Masaki")
    street_address = models.CharField(max_length=255, blank=True)
    preferred_language = models.CharField(
        max_length=10,
        choices=[("sw", "Kiswahili"), ("en", "English")],
        default="sw"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_profiles"
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")

    def __str__(self):
        return f"Profile<{self.user}>"


class SellerProfile(models.Model):
    """
    Business and merchant store profile that unlocks marketplace product publishing,
    storefront page, physical store location, and seller verification.
    """
    VERIFICATION_UNVERIFIED = "UNVERIFIED"
    VERIFICATION_PENDING = "PENDING"
    VERIFICATION_VERIFIED = "VERIFIED"
    VERIFICATION_REJECTED = "REJECTED"

    VERIFICATION_STATUS_CHOICES = [
        (VERIFICATION_UNVERIFIED, "Unverified / Haijathibitishwa"),
        (VERIFICATION_PENDING, "Pending Review / Inasubiri Uhakiki"),
        (VERIFICATION_VERIFIED, "Verified / Imethibitishwa"),
        (VERIFICATION_REJECTED, "Rejected / Imekataliwa"),
    ]

    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE,
        related_name="seller_profile"
    )
    business_name = models.CharField(max_length=150, unique=True, db_index=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    tagline = models.CharField(max_length=255, blank=True, help_text="Short business pitch or slogan")
    description = models.TextField(blank=True, help_text="Store description, return policies, warranty info")

    business_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_tz_phone],
        help_text="Direct calling phone line"
    )
    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_tz_phone],
        help_text="WhatsApp business line for direct chats"
    )

    region = models.CharField(max_length=100, default="Dar es Salaam", db_index=True)
    district = models.CharField(max_length=100, blank=True, db_index=True)
    ward = models.CharField(max_length=100, blank=True)
    street_address = models.CharField(max_length=255, blank=True, help_text="e.g. Mtaa wa Aggrey / Kongo")

    logo = models.ImageField(upload_to="sellers/logos/", null=True, blank=True)
    banner = models.ImageField(upload_to="sellers/banners/", null=True, blank=True)

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default=VERIFICATION_UNVERIFIED,
        db_index=True
    )
    national_id_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="National Identification (NIDA) or TRA TIN number"
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal("0.00"))
    reviews_count = models.PositiveIntegerField(default=0)
    is_trusted = models.BooleanField(default=False, help_text="Badge for high-volume verified honest sellers")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_seller_profiles"
        verbose_name = _("Seller Profile")
        verbose_name_plural = _("Seller Profiles")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.business_name} ({self.get_verification_status_display()})"

    @property
    def is_verified(self) -> bool:
        return self.verification_status == self.VERIFICATION_VERIFIED

    @property
    def clean_whatsapp(self) -> str:
        """Standardizes whatsapp number digits for direct wa.me/255XXXXXXXXX URL integration"""
        raw = self.whatsapp_number or self.business_phone or ""
        cleaned = "".join(filter(str.isdigit, raw))
        if cleaned.startswith("0") and len(cleaned) == 10:
            return "255" + cleaned[1:]
        elif cleaned.startswith("255"):
            return cleaned
        return cleaned

    def clean(self):
        super().clean()
        if self.business_phone:
            self.business_phone = normalize_tz_phone(self.business_phone)
        if self.whatsapp_number:
            self.whatsapp_number = normalize_tz_phone(self.whatsapp_number)

    def save(self, *args, **kwargs):
        self.clean()
        if not self.slug:
            base = slugify(self.business_name) or "seller"
            slug = base
            counter = 1
            while SellerProfile.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class PhoneVerificationOTP(models.Model):
    """
    Time-limited One-Time Password for verifying Tanzanian mobile phone numbers.
    Expires in 5 minutes with maximum 5 attempts.
    """
    phone_number = models.CharField(max_length=20, db_index=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "users_phone_otps"
        verbose_name = _("Phone Verification OTP")
        verbose_name_plural = _("Phone Verification OTPs")
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP for {self.phone_number} ({'used' if self.is_used else 'active'})"

    def is_valid(self, code: str) -> bool:
        from django.utils import timezone
        if self.is_used or timezone.now() > self.expires_at:
            return False
        if self.attempts >= 5:
            return False
        return self.otp_code == code

