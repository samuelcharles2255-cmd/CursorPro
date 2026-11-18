from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from . import api_views

app_name = "marketplace"

router = DefaultRouter()
router.register("locations", api_views.DarLocationViewSet, basename="api-location")
router.register("categories", api_views.CategoryViewSet, basename="api-category")
router.register("sellers", api_views.BusinessProfileViewSet, basename="api-seller")
router.register("listings", api_views.ListingViewSet, basename="api-listing")
router.register("orders", api_views.OrderViewSet, basename="api-order")
router.register("chats", api_views.ConversationViewSet, basename="api-chat")

urlpatterns = [
    # Public Marketplace Pages
    path("", views.home, name="home"),
    path("search/", views.listing_list, name="listing_list"),
    path("listing/<slug:slug>/", views.listing_detail, name="listing_detail"),
    path("listing/<slug:slug>/contact-click/", views.track_contact_click, name="track_contact_click"),

    # Language Toggle (Swahili / English)
    path("lang/", views.set_language_preference, name="set_language"),

    # Phone OTP Authentication
    path("auth/phone/", views.phone_auth_request, name="phone_auth_request"),
    path("auth/verify/", views.phone_auth_verify, name="phone_auth_verify"),
    path("auth/logout/", views.auth_logout, name="auth_logout"),

    # Seller Onboarding & Dashboard
    path("seller/register/", views.seller_register, name="seller_register"),
    path("seller/dashboard/", views.seller_dashboard, name="seller_dashboard"),
    path("seller/listings/new/", views.seller_listing_create, name="seller_listing_create"),
    path("seller/listings/<int:pk>/edit/", views.seller_listing_edit, name="seller_listing_edit"),
    path("seller/listings/<int:pk>/delete/", views.seller_listing_delete, name="seller_listing_delete"),
    path("seller/listings/<int:pk>/renew/", views.seller_listing_renew, name="seller_listing_renew"),
    path("seller/listings/<int:pk>/mark-sold/", views.seller_listing_mark_sold, name="seller_listing_mark_sold"),
    path("seller/verification/", views.seller_verification_submit, name="seller_verification"),
    path("seller/orders/<int:pk>/status/", views.seller_order_update_status, name="seller_order_status"),
    path("seller/<slug:slug>/", views.seller_store_detail, name="seller_store_detail"),

    # Shopping Cart & Direct Orders
    path("cart/", views.cart_view, name="cart_view"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.order_checkout, name="checkout"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<str:order_number>/", views.order_detail, name="order_detail"),

    # Direct In-App Chat
    path("chat/start/<int:listing_id>/", views.chat_start, name="chat_start"),
    path("chat/inbox/", views.chat_inbox, name="chat_inbox"),
    path("chat/<int:conversation_id>/", views.chat_detail, name="chat_detail"),

    # Social & Community Actions
    path("favorite/<int:pk>/", views.favorite_toggle, name="favorite_toggle"),
    path("follow/<int:seller_id>/", views.follow_toggle, name="follow_toggle"),
    path("report/<int:pk>/", views.report_listing, name="report_listing"),

    # Privacy & Tanzania PDPA 2022
    path("privacy/", views.privacy_policy, name="privacy_policy"),
    path("privacy/export-data/", views.data_export, name="data_export"),

    # PWA
    path("manifest.json", views.pwa_manifest, name="pwa_manifest"),
    path("sw.js", views.pwa_service_worker, name="pwa_sw"),

    # REST API
    path("api/", include(router.urls)),
]
