import uuid
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.marketplace.categories.models import Category, Subcategory
from apps.marketplace.listings.models import Listing, Order, OrderItem
from users.models import UserProfile, SellerProfile

UserModel = get_user_model()


class OrderAndListingActionsAPITests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Luxury Horology", icon="watch")
        self.subcategory = Subcategory.objects.create(category=self.category, name="Chronographs")

        self.seller = UserModel.objects.create_user(
            username="seller_user",
            email="seller@atrium.test",
            phone_number="+255712000111",
            password="StrongPassword123!",
            role="seller"
        )
        self.buyer = UserModel.objects.create_user(
            username="buyer_user",
            email="buyer@atrium.test",
            phone_number="+255712000222",
            password="StrongPassword123!"
        )
        self.moderator = UserModel.objects.create_user(
            username="mod_user",
            email="mod@atrium.test",
            password="StrongPassword123!",
            is_staff=True
        )

        UserProfile.objects.get_or_create(user=self.seller, defaults={"region": "Dar es Salaam"})
        UserProfile.objects.get_or_create(user=self.buyer, defaults={"region": "Arusha"})
        SellerProfile.objects.get_or_create(
            user=self.seller,
            defaults={"business_name": "Atrium Timepieces", "region": "Dar es Salaam", "district": "Ilala"}
        )

        self.listing = Listing.objects.create(
            seller=self.seller,
            category=self.category,
            subcategory=self.subcategory,
            title="Patek Philippe Nautilus 5711/1A",
            slug="patek-philippe-nautilus-5711-1a",
            description="Stainless steel, blue dial, complete with box and papers.",
            price=Decimal("125000000.00"),
            condition="LIKE_NEW",
            region="Dar es Salaam",
            status=Listing.STATUS_ACTIVE
        )

    def test_lookup_listing_by_slug_and_id(self):
        # Lookup by ID
        res_id = self.client.get(f"/api/listings/{self.listing.id}/")
        self.assertEqual(res_id.status_code, status.HTTP_200_OK)
        self.assertEqual(res_id.data["title"], self.listing.title)

        # Lookup by Slug
        res_slug = self.client.get(f"/api/listings/{self.listing.slug}/")
        self.assertEqual(res_slug.status_code, status.HTTP_200_OK)
        self.assertEqual(res_slug.data["id"], self.listing.id)

        # Filter by slug in querystring
        res_filter = self.client.get(f"/api/listings/?slug={self.listing.slug}")
        self.assertEqual(res_filter.status_code, status.HTTP_200_OK)
        results = res_filter.data.get("results", res_filter.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["slug"], self.listing.slug)

    def test_listing_actions_mark_sold_and_renew(self):
        # Non-owner cannot mark sold
        self.client.force_authenticate(user=self.buyer)
        fail_res = self.client.post(f"/api/listings/{self.listing.id}/mark_sold/")
        self.assertEqual(fail_res.status_code, status.HTTP_403_FORBIDDEN)

        # Seller marks sold
        self.client.force_authenticate(user=self.seller)
        sold_res = self.client.post(f"/api/listings/{self.listing.id}/mark_sold/")
        self.assertEqual(sold_res.status_code, status.HTTP_200_OK)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.status, Listing.STATUS_SOLD)

        # Seller renews listing
        renew_res = self.client.post(f"/api/listings/{self.listing.id}/renew/")
        self.assertEqual(renew_res.status_code, status.HTTP_200_OK)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.status, Listing.STATUS_ACTIVE)

    def test_moderation_actions_approve_reject(self):
        pending_listing = Listing.objects.create(
            seller=self.seller,
            category=self.category,
            title="Rolex Daytona Cosmograph",
            description="Pending moderation check",
            price=Decimal("85000000.00"),
            status=Listing.STATUS_PENDING_REVIEW
        )

        # Regular user cannot approve
        self.client.force_authenticate(user=self.seller)
        unauth_res = self.client.post(f"/api/listings/{pending_listing.id}/approve/")
        self.assertEqual(unauth_res.status_code, status.HTTP_403_FORBIDDEN)

        # Staff can approve
        self.client.force_authenticate(user=self.moderator)
        app_res = self.client.post(f"/api/listings/{pending_listing.id}/approve/")
        self.assertEqual(app_res.status_code, status.HTTP_200_OK)
        pending_listing.refresh_from_db()
        self.assertEqual(pending_listing.status, Listing.STATUS_ACTIVE)

        # Staff can reject
        rej_res = self.client.post(f"/api/listings/{pending_listing.id}/reject/")
        self.assertEqual(rej_res.status_code, status.HTTP_200_OK)
        pending_listing.refresh_from_db()
        self.assertEqual(pending_listing.status, Listing.STATUS_REJECTED)

    def test_order_creation_and_escrow_lifecycle(self):
        self.client.force_authenticate(user=self.buyer)
        order_payload = {
            "buyer_name": "Amani Mkwawa",
            "buyer_phone": "+255712000222",
            "buyer_email": "buyer@atrium.test",
            "delivery_address": "Ocean Road, Villa 4B",
            "delivery_district": "Ilala",
            "delivery_region": "Dar es Salaam",
            "delivery_method": "courier",
            "payment_method": "mpesa",
            "items": [
                {
                    "listing_id": self.listing.id,
                    "title": self.listing.title,
                    "unit_price": "125000000.00",
                    "quantity": 1
                }
            ]
        }

        # Create Order
        res = self.client.post("/api/orders/", order_payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("order_number", res.data)
        order_number = res.data["order_number"]
        self.assertEqual(res.data["status"], "ESCROW_LOCKED")
        self.assertEqual(Decimal(str(res.data["items_total"])), Decimal("125000000.00"))
        self.assertEqual(Decimal(str(res.data["total_amount"])), Decimal("125015000.00"))

        # Retrieve Order by order_number
        get_res = self.client.get(f"/api/orders/{order_number}/")
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["order_number"], order_number)
        self.assertEqual(len(get_res.data["items"]), 1)
        self.assertEqual(get_res.data["items"][0]["title"], self.listing.title)

        # List Orders
        list_res = self.client.get("/api/orders/")
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data), 1)
        self.assertEqual(list_res.data[0]["order_number"], order_number)
