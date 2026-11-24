from django.db.models import F
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from .filters import ListingFilter
from .models import Listing, ListingImage, Order
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    ListingCreateUpdateSerializer,
    ListingDetailSerializer,
    ListingImageSerializer,
    ListingListSerializer,
    OrderSerializer,
    CreateOrderSerializer,
)


class MarketplacePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ListingViewSet(viewsets.ModelViewSet):
    """
    Standard REST ViewSet powering the marketplace listing engine.
    Supports filtering by search query, category, price, region, and condition.
    Enforces owner-only mutation, soft-deletion, and image size limits.
    """
    queryset = Listing.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = MarketplacePagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ListingFilter
    ordering_fields = ["created_at", "price", "views_count"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        qs = Listing.objects.filter(is_deleted=False).select_related(
            "seller", "category", "subcategory"
        ).prefetch_related("images", "attributes")

        # Public list: show only active, non-expired listings
        if self.action == "list":
            # If authenticated user asks for their own listings with ?my_listings=true
            if self.request.query_params.get("my_listings") == "true" and user.is_authenticated:
                return qs.filter(seller=user)
            return qs.filter(status=Listing.STATUS_ACTIVE)

        # For detail / retrieve / update / delete
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ListingListSerializer
        elif self.action in ["retrieve"]:
            return ListingDetailSerializer
        return ListingCreateUpdateSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        val = self.kwargs[lookup_url_kwarg]
        if str(val).isdigit():
            obj = get_object_or_404(queryset, **{self.lookup_field: val})
        else:
            obj = get_object_or_404(queryset, slug__iexact=str(val))
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment views count
        Listing.objects.filter(pk=instance.pk).update(views_count=F("views_count") + 1)
        instance.refresh_from_db(fields=["views_count"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        """Soft-deletes the listing so it disappears from public listings while retaining history"""
        instance.soft_delete()

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, IsOwnerOrReadOnly],
        parser_classes=[MultiPartParser, FormParser]
    )
    def upload_image(self, request, pk=None):
        listing = self.get_object()
        self.check_object_permissions(request, listing)

        file = request.FILES.get("image")
        if not file:
            return Response({"error": "No image file provided in 'image' field."}, status=status.HTTP_400_BAD_REQUEST)

        is_primary = request.data.get("is_primary", "false").lower() in ("true", "1")
        order = int(request.data.get("order", 0))

        image_obj = ListingImage.objects.create(
            listing=listing,
            image=file,
            is_primary=is_primary,
            order=order
        )
        return Response(ListingImageSerializer(image_obj).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def mark_sold(self, request, pk=None):
        listing = self.get_object()
        if listing.seller != request.user and not request.user.is_staff:
            return Response({"error": "You do not have permission to modify this listing."}, status=status.HTTP_403_FORBIDDEN)
        listing.mark_sold()
        return Response(ListingDetailSerializer(listing, context={"request": request}).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def renew(self, request, pk=None):
        listing = self.get_object()
        if listing.seller != request.user and not request.user.is_staff:
            return Response({"error": "You do not have permission to renew this listing."}, status=status.HTTP_403_FORBIDDEN)
        listing.renew()
        return Response(ListingDetailSerializer(listing, context={"request": request}).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        listing = self.get_object()
        listing.status = Listing.STATUS_ACTIVE
        listing.save(update_fields=["status", "updated_at"])
        return Response(ListingDetailSerializer(listing, context={"request": request}).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        listing = self.get_object()
        listing.status = Listing.STATUS_REJECTED
        listing.save(update_fields=["status", "updated_at"])
        return Response(ListingDetailSerializer(listing, context={"request": request}).data)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for placing and retrieving Escrow orders.
    POST /api/orders/                -> Create an order with items & delivery
    GET  /api/orders/                -> User's placed orders
    GET  /api/orders/<order_number>/ -> Full order detail with tracking
    """
    queryset = Order.objects.all().prefetch_related("items")
    lookup_field = "order_number"
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                return Order.objects.all().prefetch_related("items")
            return Order.objects.filter(buyer=user).prefetch_related("items")
        return Order.objects.all().prefetch_related("items")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        out_serializer = OrderSerializer(order, context={"request": request})
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)

