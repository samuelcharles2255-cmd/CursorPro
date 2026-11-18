from rest_framework import serializers
from .models import (
    Category, BusinessProfile, Listing, ListingImage,
    Order, OrderItem, Conversation, ChatMessage, DarLocation
)


class DarLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DarLocation
        fields = ["id", "district", "ward_name", "is_commercial_hub"]


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id", "name_en", "name_sw", "slug", "icon", "display_order",
            "is_featured", "attribute_schema", "children"
        ]

    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data


class BusinessProfileSerializer(serializers.ModelSerializer):
    is_verified = serializers.BooleanField(read_only=True)
    clean_whatsapp = serializers.CharField(read_only=True)

    class Meta:
        model = BusinessProfile
        fields = [
            "id", "business_name", "slug", "tagline", "description",
            "phone_number", "whatsapp_number", "clean_whatsapp", "district",
            "ward", "street_address", "landmark_directions", "google_maps_url",
            "logo", "banner", "verification_status", "is_verified",
            "total_views", "total_contacts", "created_at"
        ]


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ["id", "image", "is_cover", "order"]


class ListingListSerializer(serializers.ModelSerializer):
    cover_image = serializers.CharField(read_only=True)
    seller_name = serializers.CharField(source="seller.business_name", read_only=True)
    seller_is_verified = serializers.BooleanField(source="seller.is_verified", read_only=True)
    category_name_en = serializers.CharField(source="category.name_en", read_only=True)
    category_name_sw = serializers.CharField(source="category.name_sw", read_only=True)

    class Meta:
        model = Listing
        fields = [
            "id", "title", "slug", "price", "is_negotiable", "condition",
            "district", "ward", "status", "cover_image", "seller_name",
            "seller_is_verified", "category_name_en", "category_name_sw",
            "views_count", "created_at", "last_renewed_at"
        ]


class ListingDetailSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    seller = BusinessProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Listing
        fields = [
            "id", "title", "slug", "description", "price", "is_negotiable",
            "condition", "district", "ward", "pickup_available", "delivery_available",
            "attributes", "status", "views_count", "contact_clicks_count",
            "favorites_count", "created_at", "last_renewed_at", "seller",
            "category", "images"
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "listing", "product_title", "unit_price", "quantity", "total_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    business_name = serializers.CharField(source="business.business_name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "status", "fulfillment_type", "customer_name",
            "customer_phone", "delivery_district", "delivery_ward", "delivery_address",
            "notes", "total_amount", "business_name", "items", "created_at"
        ]


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source="sender.email", read_only=True)

    class Meta:
        model = ChatMessage
        fields = ["id", "conversation", "sender", "sender_email", "text", "is_read", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source="business.business_name", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id", "customer", "customer_email", "business", "business_name",
            "listing", "created_at", "updated_at", "last_message"
        ]

    def get_last_message(self, obj):
        msg = obj.messages.last()
        return ChatMessageSerializer(msg).data if msg else None
