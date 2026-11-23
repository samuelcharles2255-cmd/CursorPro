from django.contrib import admin
from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "listing", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email", "listing__title")
    readonly_fields = ("created_at",)
