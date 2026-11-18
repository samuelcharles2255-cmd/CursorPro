import os
import uuid
import secrets
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image
import io
from django.core.files.base import ContentFile


# ==========================================
# 1. DAR ES SALAAM LOCATIONS
# ==========================================

DAR_DISTRICT_CHOICES = [
    ("ilala", "Ilala"),
    ("kinondoni", "Kinondoni"),
    ("temeke", "Temeke"),
    ("ubungo", "Ubungo"),
    ("kigamboni", "Kigamboni"),
]

DAR_WARDS_BY_DISTRICT = {
    "ilala": [
        "Kariakoo", "Posta / Kisutu", "Gerezani", "Upanga Mashariki", "Upanga Magharibi",
        "Jangwani", "Mchafukoge", "Buguruni", "Vingunguti", "Tabata", "Segerea",
        "Kinyerezi", "Ukonga", "Gongo la Mboto", "Chanika", "Kitunda", "Kipawa"
    ],
    "kinondoni": [
        "Masaki", "Oysterbay", "Mikocheni", "Msasani", "Sinza", "Mwenge", "Kijitonyama",
        "Kinondoni", "Magomeni", "Mwananyamala", "Tandale", "Kawe", "Mbezi Beach",
        "Tegeta", "Kunduchi", "Boko", "Wazo", "Kigogo"
    ],
    "temeke": [
        "Mbagala", "Mbagala Kuu", "Chang'ombe", "Kurasini", "Temeke", "Keko",
        "Yombo Vituka", "Sandali", "Tandika", "Mtoni", "Buza", "Chamazi", "Toangoma"
    ],
    "ubungo": [
        "Ubungo", "Mlimani / University", "Manzese", "Sinza", "Kimara", "Mbezi Luis",
        "Goba", "Makumbusho", "Kibamba", "Mburahati", "Mabibo", "Kwashiku"
    ],
    "kigamboni": [
        "Kigamboni", "Kijichi", "Mjimwema", "Tungi", "Kibada", "Somangila",
        "Kisarawe II", "Pembamnazi"
    ],
}


class DarLocation(models.Model):
    """Reference model for wards and districts across Dar es Salaam"""
    district = models.CharField(max_length=50, choices=DAR_DISTRICT_CHOICES)
    ward_name = models.CharField(max_length=100)
    is_commercial_hub = models.BooleanField(default=False)

    class Meta:
        db_table = "marketplace_dar_locations"
        unique_together = ("district", "ward_name")
        ordering = ["district", "ward_name"]

    def __str__(self):
        return f"{self.ward_name} ({self.get_district_display()})"


# ==========================================
# 2. CATEGORIES & DYNAMIC ATTRIBUTES
# ==========================================

class Category(models.Model):
    """Hierarchical category tree with category-specific attribute definitions"""
    name_en = models.CharField(max_length=100)
    name_sw = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )
    icon = models.CharField(
        max_length=50,
        default="tag",
        help_text="Icon identifier (e.g. smartphone, laptop, shopping-bag, car, home)"
    )
    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    # JSON schema defining extra attributes needed for listings in this category.
    # Example format:
    # [
    #   {"key": "brand", "label_en": "Brand", "label_sw": "Chapa", "type": "select", "options": ["Apple", "Samsung", "Tecno", "Infinix"]},
    #   {"key": "storage", "label_en": "Storage", "label_sw": "Uwezo wa Kumbukumbu", "type": "select", "options": ["64GB", "128GB", "256GB"]}
    # ]
    attribute_schema = models.JSONField(
        default=list,
        blank=True,
        help_text="List of attribute definitions for listings in this category"
    )

    class Meta:
        db_table = "marketplace_categories"
        verbose_name_plural = "Categories"
        ordering = ["display_order", "name_en"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name_en} > {self.name_en}"
        return self.name_en

    def name_for(self, lang="sw"):
        return self.name_sw if lang == "sw" and self.name_sw else self.name_en

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)


# ==========================================
# 3. BUSINESS PROFILE & SELLER VERIFICATION
# ==========================================

class BusinessProfile(models.Model):
    """Business owner profile that unlocks seller features, store page, and product publishing"""
    VERIFICATION_UNVERIFIED = "unverified"
    VERIFICATION_PENDING = "pending"
    VERIFICATION_VERIFIED = "verified"
    VERIFICATION_REJECTED = "rejected"

    VERIFICATION_STATUS_CHOICES = [
        (VERIFICATION_UNVERIFIED, "Unverified / Haijathibitishwa"),
        (VERIFICATION_PENDING, "Pending Review / Inasubiri Uhakiki"),
        (VERIFICATION_VERIFIED, "Verified / Imethibitishwa"),
        (VERIFICATION_REJECTED, "Rejected / Imekataliwa"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="marketplace_business"
    )
    business_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    tagline = models.CharField(max_length=255, blank=True, help_text="Short slogan or summary")
    description = models.TextField(blank=True, help_text="About the business, warranties, delivery policy")

    phone_number = models.CharField(max_length=30, help_text="Call line (e.g., 0712345678 or +255712345678)")
    whatsapp_number = models.CharField(max_length=30, blank=True, help_text="WhatsApp line for direct chats")

    # Dar es Salaam Location Details
    district = models.CharField(max_length=50, choices=DAR_DISTRICT_CHOICES, default="ilala")
    ward = models.CharField(max_length=100, default="Kariakoo")
    street_address = models.CharField(max_length=255, blank=True, help_text="e.g. Mtaa wa Kongo / Aggrey")
    landmark_directions = models.TextField(
        blank=True,
        help_text="Clear directions for buyers to reach the physical shop"
    )
    google_maps_url = models.URLField(blank=True, null=True, help_text="Link to Google Maps pin")

    logo = models.ImageField(upload_to="marketplace/logos/", blank=True, null=True)
    banner = models.ImageField(upload_to="marketplace/banners/", blank=True, null=True)

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default=VERIFICATION_UNVERIFIED
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    # Metrics & Counter Cache
    total_views = models.PositiveIntegerField(default=0)
    total_contacts = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "marketplace_businesses"
        ordering = ["-created_at"]

    def __str__(self):
        return self.business_name

    @property
    def is_verified(self):
        return self.verification_status == self.VERIFICATION_VERIFIED

    @property
    def clean_whatsapp(self):
        """Format number for wa.me links (+255 or 255...)"""
        raw = self.whatsapp_number or self.phone_number or ""
        cleaned = "".join(filter(str.isdigit, raw))
        if cleaned.startswith("0") and len(cleaned) == 10:
            return "255" + cleaned[1:]
        elif cleaned.startswith("255"):
            return cleaned
        return cleaned

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.business_name) or "shop"
            candidate = base_slug
            idx = 1
            while BusinessProfile.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{idx}"
                idx += 1
            self.slug = candidate
        super().save(*args, **kwargs)


class SellerVerification(models.Model):
    """Official ID and business documentation submission for manual review"""
    DOC_NIDA = "nida"
    DOC_VOTER = "voter_id"
    DOC_PASSPORT = "passport"
    DOC_DRIVING = "driving_license"
    DOC_TIN = "tin_certificate"

    DOC_CHOICES = [
        (DOC_NIDA, "NIDA National ID / Kitambulisho cha Taifa"),
        (DOC_VOTER, "Voter ID / Kitambulisho cha Mpiga Kura"),
        (DOC_PASSPORT, "Passport / Pasipoti"),
        (DOC_DRIVING, "Driving License / Leseni ya Udereva"),
        (DOC_TIN, "TIN Certificate / Cheti cha TIN (TRA)"),
    ]

    business = models.OneToOneField(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name="verification_application"
    )
    document_type = models.CharField(max_length=30, choices=DOC_CHOICES, default=DOC_NIDA)
    id_number = models.CharField(max_length=100, help_text="ID or document number")
    document_front = models.ImageField(upload_to="marketplace/verification/")
    document_back = models.ImageField(upload_to="marketplace/verification/", blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=BusinessProfile.VERIFICATION_STATUS_CHOICES,
        default=BusinessProfile.VERIFICATION_PENDING
    )
    admin_notes = models.TextField(blank=True, help_text="Moderator feedback or reason for rejection")
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderated_verifications"
    )

    class Meta:
        db_table = "marketplace_seller_verifications"

    def __str__(self):
        return f"Verification<{self.business.business_name}>: {self.status}"


# ==========================================
# 4. LISTINGS & PRODUCTS
# ==========================================

class Listing(models.Model):
    """Marketplace product or service listing posted by a seller"""
    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"
    STATUS_SOLD = "sold"
    STATUS_EXPIRED = "expired"
    STATUS_SUSPENDED = "suspended"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active / Inapatikana"),
        (STATUS_SOLD, "Sold / Imeuzwa"),
        (STATUS_DRAFT, "Draft / Rasimu"),
        (STATUS_EXPIRED, "Expired / Imeisha Muda"),
        (STATUS_SUSPENDED, "Suspended / Imesitishwa"),
    ]

    CONDITION_NEW = "new"
    CONDITION_LIKE_NEW = "like_new"
    CONDITION_GOOD = "good"
    CONDITION_FAIR = "fair"

    CONDITION_CHOICES = [
        (CONDITION_NEW, "Brand New / Mpya"),
        (CONDITION_LIKE_NEW, "Used - Like New / Imetumika - Kama Mpya"),
        (CONDITION_GOOD, "Used - Good / Imetumika - Hali Nzuri"),
        (CONDITION_FAIR, "Used - Fair / Imetumika - Inafanya Kazi"),
    ]

    seller = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name="listings"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="listings"
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField(help_text="Detailed description of features, specs, condition, and warranty")

    # Pricing in Tanzanian Shillings (TZS)
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Price in TZS (TSh)")
    is_negotiable = models.BooleanField(default=False, help_text="Bei inamaongezi")

    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default=CONDITION_NEW)

    # Location specifics
    district = models.CharField(max_length=50, choices=DAR_DISTRICT_CHOICES, default="ilala")
    ward = models.CharField(max_length=100, default="Kariakoo")
    pickup_available = models.BooleanField(default=True, help_text="Inapatikana dukani moja kwa moja")
    delivery_available = models.BooleanField(default=True, help_text="Huduma ya kuletewa inapatikana")

    # Category-specific attributes stored as key-value JSON
    # e.g., {"brand": "Apple", "storage": "128GB", "ram": "6GB", "color": "Space Gray"}
    attributes = models.JSONField(default=dict, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE, db_index=True)

    # Performance & engagement counters
    views_count = models.PositiveIntegerField(default=0)
    contact_clicks_count = models.PositiveIntegerField(default=0)
    favorites_count = models.PositiveIntegerField(default=0)

    # Expiry & Renewal: Listings are active for 30 days, then can be renewed by seller
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_renewed_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    renewal_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "marketplace_listings"
        ordering = ["-last_renewed_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "category"]),
            models.Index(fields=["status", "district", "ward"]),
            models.Index(fields=["status", "-price"]),
        ]

    def __str__(self):
        return f"{self.title} - TSh {self.price:,.0f}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "listing"
            candidate = f"{base_slug}-{secrets.token_hex(3)}"
            self.slug = candidate
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE and (not self.expires_at or self.expires_at > timezone.now())

    def renew(self):
        """Seller renews listing: extends expiry by 30 days and bumps to top of feed"""
        self.last_renewed_at = timezone.now()
        self.expires_at = timezone.now() + timezone.timedelta(days=30)
        self.status = self.STATUS_ACTIVE
        self.renewal_count += 1
        self.save(update_fields=["last_renewed_at", "expires_at", "status", "renewal_count"])

    @property
    def cover_image(self):
        first_img = self.images.filter(is_cover=True).first() or self.images.first()
        return first_img.image.url if first_img and first_img.image else None


class ListingImage(models.Model):
    """Images attached to a listing (up to 8 images per listing).
    Images are compressed and optimized on save to guarantee <150KB for fast 3G loading."""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="marketplace/listings/%Y/%m/")
    is_cover = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "marketplace_listing_images"
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"Image {self.order} for {self.listing.title}"

    def save(self, *args, **kwargs):
        # Image optimization: resize and compress to keep under 150KB
        if self.image and hasattr(self.image, "file"):
            try:
                img = Image.open(self.image)
                # Convert RGBA to RGB for JPEG/WebP compression
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Resize if larger than 1200px
                max_dimension = 1200
                if img.width > max_dimension or img.height > max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

                buffer = io.BytesIO()
                # Save as JPEG with 78% quality for excellent quality and small size
                img.save(buffer, format="JPEG", quality=78, optimize=True)
                buffer.seek(0)

                filename = os.path.splitext(self.image.name)[0] + ".jpg"
                self.image = ContentFile(buffer.read(), name=filename)
            except Exception:
                pass
        super().save(*args, **kwargs)


# ==========================================
# 5. CART & ORDERS (MVP Order Management)
# ==========================================

class CartItem(models.Model):
    """Shopping cart item for customers reserving products before ordering"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="marketplace_cart_items",
        null=True,
        blank=True
    )
    session_key = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "marketplace_cart_items"
        ordering = ["-added_at"]

    @property
    def subtotal(self):
        return self.listing.price * self.quantity


class Order(models.Model):
    """Direct MVP order connecting customer and business owner"""
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_READY = "ready"
    STATUS_DELIVERING = "delivering"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending / Inasubiri Kukubaliwa"),
        (STATUS_CONFIRMED, "Confirmed / Imethibitishwa na Muuzaji"),
        (STATUS_READY, "Ready for Pickup / Tayari Kuchukuliwa"),
        (STATUS_DELIVERING, "On the Way / Imetumwa kwa Bodaboda"),
        (STATUS_COMPLETED, "Completed / Imekamilika"),
        (STATUS_CANCELLED, "Cancelled / Imefutwa"),
    ]

    FULFILLMENT_PICKUP = "pickup"
    FULFILLMENT_DELIVERY = "delivery"
    FULFILLMENT_CHOICES = [
        (FULFILLMENT_PICKUP, "Pickup at Store / Kuchukua Dukani"),
        (FULFILLMENT_DELIVERY, "Delivery in Dar / Kuletewa (Bodaboda)"),
    ]

    order_number = models.CharField(max_length=32, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="marketplace_orders"
    )
    business = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name="received_orders"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    fulfillment_type = models.CharField(max_length=20, choices=FULFILLMENT_CHOICES, default=FULFILLMENT_PICKUP)

    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=30)
    delivery_district = models.CharField(max_length=50, choices=DAR_DISTRICT_CHOICES, blank=True)
    delivery_ward = models.CharField(max_length=100, blank=True)
    delivery_address = models.CharField(max_length=255, blank=True, help_text="Mtaa, Nyumba, Maelezo")
    notes = models.TextField(blank=True, help_text="Maelekezo ya ziada kutoka kwa mteja")

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "marketplace_orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.order_number} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{secrets.token_hex(4).upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True)
    product_title = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "marketplace_order_items"

    @property
    def total_price(self):
        return self.unit_price * self.quantity


# ==========================================
# 6. IN-APP MESSAGING / CUSTOMER-SELLER CHAT
# ==========================================

class Conversation(models.Model):
    """Direct conversation thread between a customer and a seller"""
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="marketplace_customer_chats"
    )
    business = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name="marketplace_seller_chats"
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "marketplace_conversations"
        unique_together = ("customer", "business", "listing")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Chat: {self.customer.email} <-> {self.business.business_name}"


class ChatMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "marketplace_chat_messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"Message from {self.sender.email} at {self.created_at}"


# ==========================================
# 7. FAVORITES & SELLER FOLLOWS
# ==========================================

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="marketplace_favorites")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "marketplace_favorites"
        unique_together = ("user", "listing")


class SellerFollow(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following_sellers")
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "marketplace_seller_follows"
        unique_together = ("user", "business")


# ==========================================
# 8. REPORTS & MODERATION
# ==========================================

class Report(models.Model):
    REASON_SCAM = "scam"
    REASON_COUNTERFEIT = "counterfeit"
    REASON_ILLEGAL = "illegal"
    REASON_MISLEADING = "misleading"
    REASON_OFFENSIVE = "offensive"
    REASON_OTHER = "other"

    REASON_CHOICES = [
        (REASON_SCAM, "Fraud / Scam / Utapeli"),
        (REASON_COUNTERFEIT, "Counterfeit / Bidhaa Feki"),
        (REASON_ILLEGAL, "Prohibited or Illegal Item / Bidhaa Isiyoruhusiwa"),
        (REASON_MISLEADING, "Misleading Description / Maelezo ya Uongo"),
        (REASON_OFFENSIVE, "Inappropriate Content / Maudhui Yasiyofaa"),
        (REASON_OTHER, "Other Reason / Sababu Nyingine"),
    ]

    STATUS_PENDING = "pending"
    STATUS_REVIEWED = "reviewed"
    STATUS_ACTION_TAKEN = "action_taken"
    STATUS_DISMISSED = "dismissed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending Review"),
        (STATUS_REVIEWED, "Under Review"),
        (STATUS_ACTION_TAKEN, "Action Taken / Listing Suspended"),
        (STATUS_DISMISSED, "Dismissed"),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submitted_reports"
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports"
    )
    reported_business = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports"
    )

    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    explanation = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    moderator_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "marketplace_reports"
        ordering = ["-created_at"]


# ==========================================
# 9. PHONE AUTH & OTP (Tanzania SMS Auth)
# ==========================================

class PhoneOTP(models.Model):
    """Phone number OTP verification codes with rate limiting and 5-minute expiry"""
    PURPOSE_SIGNUP = "signup"
    PURPOSE_LOGIN = "login"
    PURPOSE_VERIFY = "verify"

    PURPOSE_CHOICES = [
        (PURPOSE_SIGNUP, "Signup"),
        (PURPOSE_LOGIN, "Login"),
        (PURPOSE_VERIFY, "Verify Phone"),
    ]

    phone_number = models.CharField(max_length=30, db_index=True)
    otp_code = models.CharField(max_length=8)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default=PURPOSE_LOGIN)
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "marketplace_phone_otps"
        ordering = ["-created_at"]

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at and self.attempts < 5


# ==========================================
# 10. SECURITY & TANZANIA PDPA AUDIT LOGS
# ==========================================

class AuditLog(models.Model):
    """Immutable audit log for security, admin moderation, and Tanzania PDPA 2022 compliance"""
    action = models.CharField(max_length=100)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    target_type = models.CharField(max_length=50)
    target_id = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "marketplace_audit_logs"
        ordering = ["-created_at"]
