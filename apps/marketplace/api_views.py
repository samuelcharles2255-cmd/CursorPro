from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Category, BusinessProfile, Listing, Order,
    Conversation, ChatMessage, DarLocation
)
from .serializers import (
    CategorySerializer, BusinessProfileSerializer,
    ListingListSerializer, ListingDetailSerializer,
    OrderSerializer, ConversationSerializer, ChatMessageSerializer,
    DarLocationSerializer
)


class DarLocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DarLocation.objects.all()
    serializer_class = DarLocationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["ward_name", "district"]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(parent=None).prefetch_related("children")
    serializer_class = CategorySerializer


class BusinessProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter]
    search_fields = ["business_name", "ward", "district"]


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.filter(status=Listing.STATUS_ACTIVE).select_related("seller", "category").prefetch_related("images")
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category__slug", "district", "ward", "condition"]
    search_fields = ["title", "description", "seller__business_name", "ward"]
    ordering_fields = ["price", "created_at", "last_renewed_at", "views_count"]

    def get_serializer_class(self):
        if self.action in ["retrieve", "create", "update", "partial_update"]:
            return ListingDetailSerializer
        return ListingListSerializer

    def perform_create(self, serializer):
        business = self.request.user.marketplace_business
        serializer.save(seller=business)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def renew(self, request, slug=None):
        listing = self.get_object()
        if listing.seller.user != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        listing.renew()
        return Response({"status": "renewed", "expires_at": listing.expires_at})


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(customer=user).select_related("business").prefetch_related("items")


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            customer=user
        ) | Conversation.objects.filter(business__user=user)

    @action(detail=True, methods=["post"])
    def send_message(self, request, pk=None):
        conv = self.get_object()
        text = request.data.get("text", "").strip()
        if not text:
            return Response({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)
        msg = ChatMessage.objects.create(
            conversation=conv,
            sender=request.user,
            text=text
        )
        return Response(ChatMessageSerializer(msg).data, status=status.HTTP_201_CREATED)
