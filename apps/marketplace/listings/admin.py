from django.contrib import admin
from django.utils.html import format_html
from .models import Listing, ListingImage, ListingAttribute


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    fields = ("image", "is_primary", "order", "image_preview")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; border-radius: 4px;" />', obj.image.url)
        return "-"


class ListingAttributeInline(admin.TabularInline):
    model = ListingAttribute
    extra = 2


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "title", "price", "seller", "category", "region", "district",
        "condition", "status", "is_deleted", "created_at"
    )
    list_filter = ("status", "condition", "is_deleted", "region", "category")
    search_fields = ("title", "description", "seller__email", "seller__phone_number", "region", "district")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ListingImageInline, ListingAttributeInline]
    actions = ["mark_as_active", "mark_as_sold", "soft_delete_listings"]

    @admin.action(description="Mark selected listings as Active")
    def mark_as_active(self, request, queryset):
        queryset.update(status=Listing.STATUS_ACTIVE)

    @admin.action(description="Mark selected listings as Sold")
    def mark_as_sold(self, request, queryset):
        queryset.update(status=Listing.STATUS_SOLD)

    @admin.action(description="Soft delete selected listings")
    def soft_delete_listings(self, request, queryset):
        for obj in queryset:
            obj.soft_delete()


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ("listing", "order", "is_primary", "created_at")
    list_filter = ("is_primary",)


@admin.register(ListingAttribute)
class ListingAttributeAdmin(admin.ModelAdmin):
    list_display = ("listing", "name", "value")
    search_fields = ("listing__title", "name", "value")
