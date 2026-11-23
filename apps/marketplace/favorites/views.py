from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.marketplace.listings.models import Listing
from .models import Favorite
from .serializers import FavoriteSerializer


class FavoriteListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user).select_related("listing", "listing__category")
        serializer = FavoriteSerializer(favorites, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        listing_id = request.data.get("listing_id")
        if not listing_id:
            return Response({"error": "listing_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        listing = get_object_or_404(Listing, pk=listing_id, is_deleted=False)
        favorite, created = Favorite.objects.get_or_create(user=request.user, listing=listing)

        if not created:
            # Toggle favorite: if already favorited, remove it
            favorite.delete()
            return Response({"message": "Listing removed from favorites.", "favorited": False}, status=status.HTTP_200_OK)

        return Response({
            "message": "Listing added to favorites.",
            "favorited": True,
            "data": FavoriteSerializer(favorite, context={"request": request}).data
        }, status=status.HTTP_201_CREATED)
