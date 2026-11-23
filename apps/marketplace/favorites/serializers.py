from rest_framework import serializers
from apps.marketplace.listings.serializers import ListingListSerializer
from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    listing_details = ListingListSerializer(source="listing", read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "listing", "listing_details", "created_at"]
        read_only_fields = ["id", "created_at"]
