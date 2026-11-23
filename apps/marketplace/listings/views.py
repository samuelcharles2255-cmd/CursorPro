from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from .filters import ListingFilter
from .models import Listing, ListingImage
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    ListingCreateUpdateSerializer,
    ListingDetailSerializer,
    ListingImageSerializer,
    ListingListSerializer,
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
