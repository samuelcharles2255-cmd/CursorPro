import io
from decimal import Decimal
from PIL import Image
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from .models import (
    Category, DarLocation, BusinessProfile, Listing,
    ListingImage, CartItem, Order, OrderItem,
    Conversation, ChatMessage, Report, PhoneOTP
)
from .services.sms import OTPService, normalize_tz_phone

User = get_user_model()


class MarketplaceTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create buyer user
        self.buyer = User.objects.create_user(
            username="buyer_test",
            email="buyer@example.com",
            password="password123",
            name="Juma Mnunuzi"
        )

        # Create seller user
        self.seller_user = User.objects.create_user(
            username="seller_test",
            email="seller@example.com",
            password="password123",
            name="Amina Muuzaji",
            role="employer"
        )

        # Create Business Profile in Kariakoo
        self.business = BusinessProfile.objects.create(
            user=self.seller_user,
            business_name="Kariakoo Electronics Hub",
            phone_number="0712345678",
            whatsapp_number="0712345678",
            district="ilala",
            ward="Kariakoo",
            street_address="Mtaa wa Kongo, Dar es Salaam",
            landmark_directions="Mkabala na Benki ya NMB",
            verification_status=BusinessProfile.VERIFICATION_VERIFIED
        )

        # Create Category Hierarchy
        self.parent_cat = Category.objects.create(
            name_en="Electronics",
            name_sw="Vifaa vya Kielektroniki",
            slug="electronics",
            is_featured=True
        )

        self.sub_cat = Category.objects.create(
            parent=self.parent_cat,
            name_en="Smartphones",
            name_sw="Simu Janja",
            slug="smartphones",
            attribute_schema=[
                {"key": "brand", "label_en": "Brand", "type": "select", "options": ["Apple", "Samsung"]},
                {"key": "storage", "label_en": "Storage", "type": "select", "options": ["128GB", "256GB"]}
            ]
        )

        # Create Listing
        self.listing = Listing.objects.create(
            seller=self.business,
            category=self.sub_cat,
            title="iPhone 14 Pro Max 256GB",
            description="Simu mpya kabisa yenye warranty ya mwaka mmoja.",
            price=Decimal("2100000.00"),
            is_negotiable=True,
            condition=Listing.CONDITION_NEW,
            district="ilala",
            ward="Kariakoo",
            attributes={"brand": "Apple", "storage": "256GB"}
        )

    def test_phone_normalization_and_otp(self):
        """Test Tanzanian phone normalization and OTP service"""
        # Test 07... normalization
        self.assertEqual(normalize_tz_phone("0712345678"), "+255712345678")
        # Test +255...
        self.assertEqual(normalize_tz_phone("+255 712 345 678"), "+255712345678")

        # Send OTP
        res = OTPService.send_otp("0712345678", purpose=PhoneOTP.PURPOSE_LOGIN)
        self.assertTrue(res["success"])
        self.assertEqual(res["phone_number"], "+255712345678")

        otp_record = PhoneOTP.objects.filter(phone_number="+255712345678").first()
        self.assertIsNotNone(otp_record)
        self.assertTrue(otp_record.is_valid())

        # Verify with correct code
        verify_res = OTPService.verify_otp("+255712345678", otp_record.otp_code, purpose=PhoneOTP.PURPOSE_LOGIN)
        self.assertTrue(verify_res["success"])

        # Record should now be marked as used
        otp_record.refresh_from_db()
        self.assertTrue(otp_record.is_used)

    def test_listing_renewal_bumps_time(self):
        """Test renewal mechanism resets 30-day expiry and bumps last_renewed_at"""
        old_renewed = self.listing.last_renewed_at
        self.assertEqual(self.listing.renewal_count, 0)

        self.listing.renew()
        self.listing.refresh_from_db()

        self.assertEqual(self.listing.renewal_count, 1)
        self.assertGreaterEqual(self.listing.last_renewed_at, old_renewed)
        self.assertGreater(self.listing.expires_at, timezone.now())

    def test_home_page_renders_cleanly(self):
        """Test marketplace home page renders with listings and categories"""
        response = self.client.get(reverse("marketplace:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kariakoo")
        self.assertContains(response, "iPhone 14 Pro Max")

    def test_search_and_filters(self):
        """Test search query, category filtering, and ward filtering"""
        # Search by keyword
        resp = self.client.get(reverse("marketplace:listing_list"), {"q": "iPhone"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "iPhone 14 Pro Max")

        # Filter by ward
        resp_ward = self.client.get(reverse("marketplace:listing_list"), {"ward": "Kariakoo"})
        self.assertEqual(resp_ward.status_code, 200)
        self.assertContains(resp_ward, "iPhone 14 Pro Max")

        # Filter by non-existent ward
        resp_empty = self.client.get(reverse("marketplace:listing_list"), {"ward": "Kigamboni"})
        self.assertEqual(resp_empty.status_code, 200)
        self.assertEqual(len(resp_empty.context["listings"]), 0)

    def test_cart_and_order_flow(self):
        """Test adding item to cart and placing order"""
        self.client.force_login(self.buyer)

        # Add to cart
        add_resp = self.client.post(reverse("marketplace:cart_add", kwargs={"pk": self.listing.pk}), {"quantity": 1})
        self.assertEqual(add_resp.status_code, 302)

        self.assertEqual(CartItem.objects.filter(user=self.buyer).count(), 1)

        # Place order
        checkout_resp = self.client.post(reverse("marketplace:checkout"), {
            "customer_name": "Juma Mnunuzi",
            "customer_phone": "0755123456",
            "fulfillment_type": Order.FULFILLMENT_PICKUP,
            "delivery_ward": "Sinza",
            "notes": "Nitakuja kuchukua saa 10 jioni"
        })
        self.assertEqual(checkout_resp.status_code, 302)

        # Order created and cart cleared
        order = Order.objects.filter(customer=self.buyer).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.business, self.business)
        self.assertEqual(order.total_amount, Decimal("2100000.00"))
        self.assertEqual(CartItem.objects.filter(user=self.buyer).count(), 0)

    def test_in_app_chat_thread(self):
        """Test buyer and seller in-app conversation"""
        self.client.force_login(self.buyer)

        # Start chat
        start_resp = self.client.get(reverse("marketplace:chat_start", kwargs={"listing_id": self.listing.pk}))
        self.assertEqual(start_resp.status_code, 302)

        conv = Conversation.objects.filter(customer=self.buyer, business=self.business).first()
        self.assertIsNotNone(conv)

        # Send message
        msg_resp = self.client.post(
            reverse("marketplace:chat_detail", kwargs={"conversation_id": conv.pk}),
            {"message": "Habari, simu hii inakuja na risiti ya EFD?"}
        )
        self.assertEqual(msg_resp.status_code, 302)

        self.assertEqual(conv.messages.count(), 1)
        self.assertEqual(conv.messages.first().text, "Habari, simu hii inakuja na risiti ya EFD?")

    def test_tanzania_pdpa_data_export(self):
        """Test user data export endpoint compliance with Tanzania PDPA 2022"""
        self.client.force_login(self.buyer)
        resp = self.client.get(reverse("marketplace:data_export"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/json")
        self.assertIn("Personal Data Protection Act", resp.content.decode())

    def test_rest_api_listings(self):
        """Test REST API endpoint for listings"""
        resp = self.client.get("/marketplace/api/listings/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        results = data["results"] if isinstance(data, dict) and "results" in data else data
        self.assertGreaterEqual(len(results), 1)
