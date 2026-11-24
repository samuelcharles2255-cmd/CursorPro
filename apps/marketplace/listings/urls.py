from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ListingViewSet, OrderViewSet
from apps.marketplace.categories.views import CategoryViewSet

router = DefaultRouter()
router.register("listings", ListingViewSet, basename="listing")
router.register("categories", CategoryViewSet, basename="category")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
]
