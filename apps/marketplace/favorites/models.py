from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Favorite(models.Model):
    """
    Saved / bookmarked listing saved by an authenticated user.
    Enforces uniqueness so a user can bookmark a listing only once.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name=_("user")
    )
    listing = models.ForeignKey(
        "listings.Listing",
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name=_("listing")
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "favorites_favorite"
        verbose_name = _("Favorite")
        verbose_name_plural = _("Favorites")
        unique_together = ("user", "listing")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"], name="idx_fav_user_created"),
            models.Index(fields=["listing", "-created_at"], name="idx_fav_listing_created"),
        ]

    def __str__(self):
        return f"{self.user} saved {self.listing.title}"
