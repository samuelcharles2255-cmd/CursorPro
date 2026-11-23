from decimal import Decimal
from rest_framework import serializers

from apps.marketplace.categories.models import Category, Subcategory
from .models import Listing, ListingImage, ListingAttribute


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ["id", "image", "is_primary", "order", "created_at"]
        read_only_fields = ["id", "created_at"]


class ListingAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingAttribute
        fields = ["id", "name", "value"]
        read_only_fields = ["id"]


class ListingListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    primary_image_url = serializers.SerializerMethodField()
    seller_name = serializers.CharField(source="seller.username", read_only=True)

    class Meta:
        model = Listing
        fields = [
            "id", "title", "slug", "price", "is_negotiable",
            "category", "category_name", "category_slug",
            "region", "district", "condition", "status",
            "primary_image_url", "seller_name", "views_count",
            "created_at"
        ]

    def get_primary_image_url(self, obj):
        prim = obj.primary_image
        if prim and prim.image:
            request = self.context.get("request")
            return request.build_absolute_uri(prim.image.url) if request else prim.image.url
        return None


class ListingDetailSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    attributes = ListingAttributeSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    subcategory_name = serializers.CharField(source="subcategory.name", read_only=True, default=None)
    seller_id = serializers.IntegerField(source="seller.id", read_only=True)
    seller_username = serializers.CharField(source="seller.username", read_only=True)
    seller_phone = serializers.CharField(source="seller.phone_number", read_only=True)

    class Meta:
        model = Listing
        fields = [
            "id", "title", "slug", "description", "price", "is_negotiable",
            "category", "category_name", "subcategory", "subcategory_name",
            "condition", "status", "region", "district", "ward",
            "street_address", "pickup_available", "delivery_available",
            "views_count", "seller_id", "seller_username", "seller_phone",
            "images", "attributes", "created_at", "updated_at", "expires_at"
        ]


class ListingCreateUpdateSerializer(serializers.ModelSerializer):
    attributes_data = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        required=False,
        write_only=True,
        help_text="Optional key-value attributes: [{'name': 'Storage', 'value': '128GB'}]"
    )

    class Meta:
        model = Listing
        fields = [
            "id", "title", "description", "price", "is_negotiable",
            "category", "subcategory", "condition", "status",
            "region", "district", "ward", "street_address",
            "pickup_available", "delivery_available", "attributes_data"
        ]
        read_only_fields = ["id"]

    def validate_price(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("Price must be a positive number greater than 0.")
        return value

    def create(self, validated_data):
        attributes_data = validated_data.pop("attributes_data", None)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["seller"] = request.user

        listing = super().create(validated_data)

        if attributes_data:
            for item in attributes_data:
                name = item.get("name")
                val = item.get("value")
                if name and val:
                    ListingAttribute.objects.create(listing=listing, name=name, value=val)

        return listing

    def update(self, instance, validated_data):
        attributes_data = validated_data.pop("attributes_data", None)
        listing = super().update(instance, validated_data)

        if attributes_data is not None:
            # Overwrite or upsert attributes
            listing.attributes.all().delete()
            for item in attributes_data:
                name = item.get("name")
                val = item.get("value")
                if name and val:
                    ListingAttribute.objects.create(listing=listing, name=name, value=val)

        return listing
