from decimal import Decimal
import secrets
from rest_framework import serializers

from apps.marketplace.categories.models import Category, Subcategory
from .models import Listing, ListingImage, ListingAttribute, Order, OrderItem


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
    seller_name = serializers.SerializerMethodField()
    seller_username = serializers.CharField(source="seller.username", read_only=True)
    seller_phone = serializers.CharField(source="seller.phone_number", read_only=True)
    primary_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "id", "title", "slug", "description", "price", "is_negotiable",
            "category", "category_name", "subcategory", "subcategory_name",
            "condition", "status", "region", "district", "ward",
            "street_address", "pickup_available", "delivery_available",
            "views_count", "seller_id", "seller_name", "seller_username", "seller_phone",
            "primary_image_url", "images", "attributes", "created_at", "updated_at", "expires_at"
        ]

    def get_seller_name(self, obj):
        if hasattr(obj.seller, "name") and obj.seller.name:
            return obj.seller.name
        return obj.seller.username

    def get_primary_image_url(self, obj):
        prim = obj.primary_image
        if prim and prim.image:
            request = self.context.get("request")
            return request.build_absolute_uri(prim.image.url) if request else prim.image.url
        return None


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


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "listing", "title", "unit_price", "quantity", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "buyer", "buyer_name", "buyer_phone",
            "buyer_email", "delivery_method", "delivery_address", "delivery_district",
            "delivery_region", "payment_method", "status", "items_total",
            "delivery_fee", "total_amount", "notes", "items", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "order_number", "created_at", "updated_at"]


class CreateOrderItemInputSerializer(serializers.Serializer):
    listing_id = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(max_length=255)
    unit_price = serializers.DecimalField(max_digits=14, decimal_places=2)
    quantity = serializers.IntegerField(default=1, min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    buyer_name = serializers.CharField(max_length=255)
    buyer_phone = serializers.CharField(max_length=30)
    buyer_email = serializers.EmailField(required=False, allow_blank=True)
    delivery_method = serializers.ChoiceField(choices=Order.DELIVERY_CHOICES, default=Order.DELIVERY_COURIER)
    delivery_address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    delivery_district = serializers.CharField(max_length=100, required=False, allow_blank=True)
    delivery_region = serializers.CharField(max_length=100, default="Dar es Salaam")
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES, default=Order.PAYMENT_MPESA)
    notes = serializers.CharField(required=False, allow_blank=True)
    items = CreateOrderItemInputSerializer(many=True)

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        if not items_data:
            raise serializers.ValidationError("An order must contain at least one item.")

        request = self.context.get("request")
        buyer = request.user if request and request.user.is_authenticated else None

        items_total = Decimal("0.00")
        for it in items_data:
            items_total += Decimal(str(it["unit_price"])) * it["quantity"]

        delivery_fee = Decimal("15000.00") if validated_data.get("delivery_method") == Order.DELIVERY_COURIER else Decimal("0.00")
        total_amount = items_total + delivery_fee
        order_num = f"AT-{secrets.token_hex(4).upper()}"

        order = Order.objects.create(
            order_number=order_num,
            buyer=buyer,
            items_total=items_total,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
            status=Order.STATUS_ESCROW_LOCKED,
            **validated_data
        )

        for it in items_data:
            listing = None
            if it.get("listing_id"):
                listing = Listing.objects.filter(pk=it["listing_id"]).first()
            OrderItem.objects.create(
                order=order,
                listing=listing,
                title=it["title"],
                unit_price=Decimal(str(it["unit_price"])),
                quantity=it["quantity"]
            )

        return order

