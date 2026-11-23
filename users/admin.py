from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile, SellerProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = _("Profile Details")


class SellerProfileInline(admin.StackedInline):
    model = SellerProfile
    can_delete = False
    verbose_name_plural = _("Seller Details")


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "phone_number", "role", "is_phone_verified", "is_staff")
    list_filter = ("role", "is_phone_verified", "is_staff", "is_superuser")
    search_fields = ("email", "username", "phone_number")
    ordering = ("-created_at",)
    inlines = [UserProfileInline, SellerProfileInline]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "phone_number")}),
        (_("Marketplace Details"), {"fields": ("role", "is_phone_verified", "is_email_verified")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "region", "district", "preferred_language", "created_at")
    search_fields = ("user__email", "user__username", "region", "district")
    list_filter = ("region", "preferred_language")


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ("business_name", "user", "region", "district", "verification_status", "rating", "is_trusted")
    list_filter = ("verification_status", "is_trusted", "region")
    search_fields = ("business_name", "user__email", "business_phone", "national_id_number")
    prepopulated_fields = {"slug": ("business_name",)}
