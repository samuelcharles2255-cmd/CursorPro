from rest_framework import serializers
from apps.marketplace.listings.models import Listing
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source="sender.id", read_only=True)
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id", "conversation", "sender_id", "sender_username",
            "content", "is_read", "read_at", "created_at"
        ]
        read_only_fields = ["id", "conversation", "is_read", "read_at", "created_at"]


class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(required=True, max_length=4000)

    def validate_content(self, value):
        text = value.strip()
        if not text:
            raise serializers.ValidationError("Message content cannot be blank or whitespace only.")
        return text


class ConversationSerializer(serializers.ModelSerializer):
    listing_id = serializers.IntegerField(source="listing.id", read_only=True)
    listing_title = serializers.CharField(source="listing.title", read_only=True)
    listing_price = serializers.DecimalField(source="listing.price", max_digits=12, decimal_places=2, read_only=True)
    buyer_id = serializers.IntegerField(source="buyer.id", read_only=True)
    buyer_username = serializers.CharField(source="buyer.username", read_only=True)
    seller_id = serializers.IntegerField(source="seller.id", read_only=True)
    seller_username = serializers.CharField(source="seller.username", read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id", "listing_id", "listing_title", "listing_price",
            "buyer_id", "buyer_username", "seller_id", "seller_username",
            "is_blocked", "last_message", "unread_count",
            "created_at", "updated_at"
        ]

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by("-created_at").first()
        if last_msg:
            return {
                "id": last_msg.id,
                "sender_id": last_msg.sender_id,
                "content": last_msg.content,
                "created_at": last_msg.created_at,
                "is_read": last_msg.is_read
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0


class CreateConversationSerializer(serializers.Serializer):
    listing_id = serializers.IntegerField(required=True)
    initial_message = serializers.CharField(required=True, max_length=4000)

    def validate_listing_id(self, value):
        listing = Listing.objects.filter(pk=value, is_deleted=False).first()
        if not listing:
            raise serializers.ValidationError("Listing does not exist or has been removed.")
        return listing

    def validate(self, attrs):
        request = self.context.get("request")
        listing = attrs["listing_id"]
        buyer = request.user

        if listing.seller == buyer:
            raise serializers.ValidationError("You cannot initiate a conversation on your own listing.")

        attrs["listing"] = listing
        attrs["buyer"] = buyer
        attrs["seller"] = listing.seller
        return attrs
