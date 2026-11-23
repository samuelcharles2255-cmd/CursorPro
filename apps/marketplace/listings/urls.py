from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ListingViewSet
from apps.marketplace.categories.views import CategoryViewSet

router = DefaultRouter()
router.register("listings", ListingViewSet, basename="listing")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = [
    path("", include(router.urls)),
]
