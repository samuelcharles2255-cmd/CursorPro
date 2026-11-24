import io
import os
import secrets
from decimal import Decimal
from PIL import Image

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .validators import validate_listing_image


class ActiveListingManager(models.Manager):
    """Queryset manager filtering for active, non-deleted, non-expired listings"""
    def get_queryset(self):
        now = timezone.now()
        return (
            super().get_queryset()
            .filter(
                is_deleted=False,
                status=Listing.STATUS_ACTIVE
            )
            .filter(
                models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
            )
        )


class Listing(models.Model):
    """
    Core marketplace listing model. Supports hierarchical categorization,
    rich attributes, geospatial regional filtering, soft-deletion, and strict status workflows.
    """
    STATUS_DRAFT = "DRAFT"
    STATUS_PENDING_REVIEW = "PENDING_REVIEW"
    STATUS_ACTIVE = "ACTIVE"
    STATUS_SOLD = "SOLD"
    STATUS_REJECTED = "REJECTED"
    STATUS_EXPIRED = "EXPIRED"

    STATUS_CHOICES = [
        (STATUS_DRAFT, _("Draft / Rasimu")),
        (STATUS_PENDING_REVIEW, _("Pending Review / Inasubiri Uhakiki")),
        (STATUS_ACTIVE, _("Active / Inapatikana")),
        (STATUS_SOLD, _("Sold / Imeuzwa")),
        (STATUS_REJECTED, _("Rejected / Imekataliwa")),
        (STATUS_EXPIRED, _("Expired / Imeisha Muda")),
    ]

    CONDITION_NEW = "NEW"
    CONDITION_LIKE_NEW = "LIKE_NEW"
    CONDITION_GOOD = "GOOD"
    CONDITION_FAIR = "FAIR"
    CONDITION_REFURBISHED = "REFURBISHED"

    CONDITION_CHOICES = [
        (CONDITION_NEW, _("Brand New / Mpya Kabisa")),
        (CONDITION_LIKE_NEW, _("Like New / Kama Mpya")),
        (CONDITION_GOOD, _("Good / Hali Nzuri")),
        (CONDITION_FAIR, _("Fair / Inafanya Kazi")),
        (CONDITION_REFURBISHED, _("Refurbished / Iliyokarabatiwa")),
    ]

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
        verbose_name=_("seller")
    )
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.PROTECT,
        related_name="listings",
        verbose_name=_("category")
    )
    subcategory = models.ForeignKey(
        "categories.Subcategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listings",
        verbose_name=_("subcategory")
    )

    title = models.CharField(_("title"), max_length=255, db_index=True)
    slug = models.SlugField(_("slug"), max_length=280, unique=True, blank=True)
    description = models.TextField(_("description"), help_text=_("Full product description, specifications, and warranty"))

    # Pricing in Tanzanian Shillings (TZS)
    price = models.DecimalField(
        _("price (TZS)"),
        max_digits=12,
        decimal_places=2,
        db_index=True,
        help_text=_("Price in Tanzanian Shillings (TSh)")
    )
    is_negotiable = models.BooleanField(_("negotiable"), default=False, help_text=_("Bei inamaongezi"))

    condition = models.CharField(
        _("condition"),
        max_length=20,
        choices=CONDITION_CHOICES,
        default=CONDITION_NEW,
        db_index=True
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        db_index=True
    )

    # Location specifics for regional search & delivery
    region = models.CharField(
        _("region"),
        max_length=100,
        db_index=True,
        help_text=_("e.g. Dar es Salaam, Mbeya, Arusha, Dodoma, Mwanza")
    )
    district = models.CharField(
        _("district"),
        max_length=100,
        db_index=True,
        help_text=_("e.g. Kinondoni, Ilala, Temeke, Mbeya Mjini")
    )
    ward = models.CharField(_("ward"), max_length=100, blank=True, help_text=_("e.g. Kariakoo, Sinza"))
    street_address = models.CharField(_("street address"), max_length=255, blank=True)

    pickup_available = models.BooleanField(_("pickup available"), default=True)
    delivery_available = models.BooleanField(_("delivery available"), default=True)

    # Performance, engagement counters & analytics
    views_count = models.PositiveIntegerField(_("views count"), default=0)

    # Soft-deletion support to maintain referential integrity without public exposure
    is_deleted = models.BooleanField(_("is deleted"), default=False, db_index=True)
    deleted_at = models.DateTimeField(_("deleted at"), null=True, blank=True)

    # Timestamps & Lifecycle management (Default 30 days expiry)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    expires_at = models.DateTimeField(_("expires at"), null=True, blank=True, db_index=True)

    objects = models.Manager()
    active = ActiveListingManager()

    class Meta:
        db_table = "listings_listing"
        verbose_name = _("Listing")
        verbose_name_plural = _("Listings")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "is_deleted", "-created_at"], name="idx_lst_stat_del_created"),
            models.Index(fields=["status", "category"], name="idx_lst_stat_cat"),
            models.Index(fields=["status", "region", "district"], name="idx_lst_stat_reg_dist"),
            models.Index(fields=["status", "price"], name="idx_lst_stat_price"),
            models.Index(fields=["status", "condition"], name="idx_lst_stat_cond"),
            models.Index(fields=["seller", "status"], name="idx_lst_seller_stat"),
        ]

    def __str__(self):
        return f"{self.title} - TSh {self.price:,.0f}"

    def soft_delete(self):
        """Soft-deletes listing so it disappears from public listings while preserving history"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def renew(self, days=30):
        """Seller renews listing: extends expiry by specified days and resets active status"""
        self.expires_at = timezone.now() + timezone.timedelta(days=days)
        self.status = self.STATUS_ACTIVE
        self.save(update_fields=["expires_at", "status", "updated_at"])

    def mark_sold(self):
        """Marks the listing as sold"""
        self.status = self.STATUS_SOLD
        self.save(update_fields=["status", "updated_at"])

    @property
    def is_active(self) -> bool:
        if self.is_deleted or self.status != self.STATUS_ACTIVE:
            return False
        if self.expires_at and self.expires_at <= timezone.now():
            return False
        return True

    @property
    def primary_image(self):
        primary = self.images.filter(is_primary=True).first()
        return primary or self.images.first()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "item"
            self.slug = f"{base_slug}-{secrets.token_hex(4)}"
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)


class ListingImage(models.Model):
    """
    Images attached to a listing. Enforces size limits and optimizes resolution to WebP/JPEG.
    """
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("listing")
    )
    image = models.ImageField(
        _("image"),
        upload_to="listings/%Y/%m/",
        validators=[validate_listing_image]
    )
    is_primary = models.BooleanField(_("primary cover image"), default=False)
    order = models.PositiveSmallIntegerField(_("display order"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "listings_image"
        verbose_name = _("Listing Image")
        verbose_name_plural = _("Listing Images")
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"Image #{self.order} for {self.listing.title}"

    def save(self, *args, **kwargs):
        # High performance image compression and optimization (<200KB for Tanzanian cellular networks)
        if self.image and hasattr(self.image, "file"):
            try:
                img = Image.open(self.image)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                max_dimension = 1400
                if img.width > max_dimension or img.height > max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80, optimize=True)
                buffer.seek(0)
                clean_name = os.path.splitext(self.image.name)[0] + ".jpg"
                self.image = ContentFile(buffer.read(), name=clean_name)
            except Exception:
                pass
        super().save(*args, **kwargs)


class ListingAttribute(models.Model):
    """
    Key-value attributes for dynamic category-specific specifications
    (e.g., Brand=Apple, Storage=256GB, RAM=8GB, Color=Space Gray, Fuel=Petrol, Year=2021).
    """
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="attributes",
        verbose_name=_("listing")
    )
    name = models.CharField(_("attribute name"), max_length=100, db_index=True)
    value = models.CharField(_("attribute value"), max_length=255)

    class Meta:
        db_table = "listings_attribute"
        verbose_name = _("Listing Attribute")
        verbose_name_plural = _("Listing Attributes")
        unique_together = ("listing", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.listing.title} -> {self.name}: {self.value}"


class Order(models.Model):
    """
    Escrow-protected marketplace order for fine goods and services.
    Supports in-person pickup and courier delivery across Tanzania.
    """
    STATUS_PENDING_PAYMENT = "PENDING_PAYMENT"
    STATUS_ESCROW_LOCKED = "ESCROW_LOCKED"
    STATUS_DISPATCHED = "DISPATCHED"
    STATUS_DELIVERED = "DELIVERED"
    STATUS_RELEASED = "RELEASED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_PENDING_PAYMENT, _("Pending Payment")),
        (STATUS_ESCROW_LOCKED, _("Escrow Locked / Funds Held")),
        (STATUS_DISPATCHED, _("Dispatched / In Transit")),
        (STATUS_DELIVERED, _("Delivered / Awaiting Inspection")),
        (STATUS_RELEASED, _("Completed / Funds Released")),
        (STATUS_CANCELLED, _("Cancelled / Refunded")),
    ]

    PAYMENT_MPESA = "mpesa"
    PAYMENT_TIGO = "tigo"
    PAYMENT_AIRTEL = "airtel"
    PAYMENT_BANK = "bank"
    PAYMENT_CHOICES = [
        (PAYMENT_MPESA, "Vodacom M-Pesa"),
        (PAYMENT_TIGO, "Tigo Pesa"),
        (PAYMENT_AIRTEL, "Airtel Money"),
        (PAYMENT_BANK, "Bank Wire / Swift"),
    ]

    DELIVERY_COURIER = "courier"
    DELIVERY_PICKUP = "pickup"
    DELIVERY_CHOICES = [
        (DELIVERY_COURIER, "Direct Courier / Express Delivery"),
        (DELIVERY_PICKUP, "Direct In-Person / Showroom Pickup"),
    ]

    order_number = models.CharField(max_length=32, unique=True, db_index=True)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="placed_orders",
        null=True,
        blank=True
    )
    buyer_name = models.CharField(max_length=255)
    buyer_phone = models.CharField(max_length=30)
    buyer_email = models.EmailField(blank=True)

    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default=DELIVERY_COURIER)
    delivery_address = models.CharField(max_length=255, blank=True)
    delivery_district = models.CharField(max_length=100, blank=True)
    delivery_region = models.CharField(max_length=100, default="Dar es Salaam")

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=PAYMENT_MPESA)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=STATUS_ESCROW_LOCKED, db_index=True)

    items_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    delivery_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "listings_order"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.order_number} - TSh {self.total_amount:,.0f} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"AT-{secrets.token_hex(4).upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True, blank=True, related_name="order_items")
    title = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "listings_order_item"

    def __str__(self):
        return f"{self.quantity}x {self.title} @ TSh {self.unit_price:,.0f}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

