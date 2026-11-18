from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    DarLocation, Category, BusinessProfile, SellerVerification,
    Listing, ListingImage, Order, OrderItem, Conversation,
    ChatMessage, Favorite, SellerFollow, Report, PhoneOTP, AuditLog
)


@admin.register(DarLocation)
class DarLocationAdmin(admin.ModelAdmin):
    list_display = ("ward_name", "district", "is_commercial_hub")
    list_filter = ("district", "is_commercial_hub")
    search_fields = ("ward_name", "district")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_sw", "parent", "slug", "display_order", "is_featured")
    list_filter = ("is_featured", "parent")
    search_fields = ("name_en", "name_sw", "slug")
    prepopulated_fields = {"slug": ("name_en",)}


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    max_num = 8


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "seller", "category", "price", "status", "condition", "district", "ward", "renewal_count", "created_at")
    list_filter = ("status", "condition", "district", "category")
    search_fields = ("title", "description", "seller__business_name", "ward")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ListingImageInline]
    actions = ["make_active", "mark_as_sold", "renew_selected"]

    def make_active(self, request, queryset):
        queryset.update(status=Listing.STATUS_ACTIVE)
    make_active.short_description = "Mark selected listings as Active"

    def mark_as_sold(self, request, queryset):
        queryset.update(status=Listing.STATUS_SOLD)
    mark_as_sold.short_description = "Mark selected listings as Sold"

    def renew_selected(self, request, queryset):
        for item in queryset:
            item.renew()
    renew_selected.short_description = "Renew selected listings (Reset 30-day timer & bump to top)"


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ("business_name", "user", "phone_number", "district", "ward", "verification_status", "total_views", "created_at")
    list_filter = ("verification_status", "district")
    search_fields = ("business_name", "user__email", "phone_number", "ward")
    prepopulated_fields = {"slug": ("business_name",)}
    actions = ["approve_verification"]

    def approve_verification(self, request, queryset):
        queryset.update(
            verification_status=BusinessProfile.VERIFICATION_VERIFIED,
            verified_at=timezone.now()
        )
    approve_verification.short_description = "Approve and grant Verified Seller badge"


@admin.register(SellerVerification)
class SellerVerificationAdmin(admin.ModelAdmin):
    list_display = ("business", "document_type", "id_number", "status", "submitted_at", "document_preview")
    list_filter = ("status", "document_type")
    search_fields = ("business__business_name", "id_number")
    readonly_fields = ("document_preview",)
    actions = ["approve_docs", "reject_docs"]

    def document_preview(self, obj):
        if obj.document_front:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="height: 50px; border-radius: 4px;"/></a>', obj.document_front.url, obj.document_front.url)
        return "No image"
    document_preview.short_description = "ID Preview"

    def approve_docs(self, request, queryset):
        now = timezone.now()
        for doc in queryset:
            doc.status = BusinessProfile.VERIFICATION_VERIFIED
            doc.reviewed_at = now
            doc.reviewed_by = request.user
            doc.save()
            # Update business
            doc.business.verification_status = BusinessProfile.VERIFICATION_VERIFIED
            doc.business.verified_at = now
            doc.business.save()
    approve_docs.short_description = "Approve selected documents and verify sellers"

    def reject_docs(self, request, queryset):
        now = timezone.now()
        for doc in queryset:
            doc.status = BusinessProfile.VERIFICATION_REJECTED
            doc.reviewed_at = now
            doc.reviewed_by = request.user
            doc.save()
            doc.business.verification_status = BusinessProfile.VERIFICATION_REJECTED
            doc.business.save()
    reject_docs.short_description = "Reject selected documents"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer", "business", "status", "fulfillment_type", "total_amount", "created_at")
    list_filter = ("status", "fulfillment_type", "created_at")
    search_fields = ("order_number", "customer__email", "business__business_name", "customer_phone")
    inlines = [OrderItemInline]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "reason", "reporter", "listing", "reported_business", "status", "created_at")
    list_filter = ("status", "reason", "created_at")
    search_fields = ("explanation", "reporter__email", "listing__title")
    actions = ["suspend_listing_and_resolve", "dismiss_report"]

    def suspend_listing_and_resolve(self, request, queryset):
        for rep in queryset:
            rep.status = Report.STATUS_ACTION_TAKEN
            rep.reviewed_at = timezone.now()
            rep.moderator_notes = f"Suspended by {request.user.email}"
            rep.save()
            if rep.listing:
                rep.listing.status = Listing.STATUS_SUSPENDED
                rep.listing.save(update_fields=["status"])
    suspend_listing_and_resolve.short_description = "Suspend flagged listings and mark resolved"

    def dismiss_report(self, request, queryset):
        queryset.update(status=Report.STATUS_DISMISSED, reviewed_at=timezone.now())
    dismiss_report.short_description = "Dismiss selected reports"


@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "otp_code", "purpose", "is_used", "attempts", "expires_at", "created_at")
    list_filter = ("purpose", "is_used")
    search_fields = ("phone_number",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "target_type", "target_id", "ip_address", "created_at")
    list_filter = ("action", "target_type")
    search_fields = ("action", "target_id", "ip_address")
