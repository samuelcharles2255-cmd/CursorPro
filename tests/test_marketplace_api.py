from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.marketplace.categories.models import Category, Subcategory
from apps.marketplace.listings.models import Listing, ListingAttribute
from apps.marketplace.messaging.models import Conversation, Message
from users.models import PhoneVerificationOTP, UserProfile, SellerProfile

UserModel = get_user_model()


def extract_results(data):
    if isinstance(data, dict) and "results" in data:
        return data["results"]
    return data


class MarketplaceFullFlowTests(APITestCase):
    def setUp(self):
        # Create categories
        self.cat_phones = Category.objects.create(name="Phones", icon="smartphone")
        self.sub_iphones = Subcategory.objects.create(category=self.cat_phones, name="iPhones")
        self.cat_vehicles = Category.objects.create(name="Vehicles", icon="car")

        # Create two test users
        self.seller = UserModel.objects.create_user(
            username="test_seller",
            email="seller@kariakoo.tz",
            phone_number="+255712111222",
            password="StrongPassword123!"
        )
        self.buyer = UserModel.objects.create_user(
            username="test_buyer",
            email="buyer@posta.tz",
            phone_number="+255754333444",
            password="StrongPassword123!"
        )
        self.intruder = UserModel.objects.create_user(
            username="test_intruder",
            email="intruder@hacker.tz",
            password="StrongPassword123!"
        )

        # Profiles
        UserProfile.objects.get_or_create(user=self.seller, defaults={"region": "Dar es Salaam", "district": "Ilala"})
        UserProfile.objects.get_or_create(user=self.buyer, defaults={"region": "Mbeya", "district": "Mbeya Mjini"})
        SellerProfile.objects.get_or_create(
            user=self.seller,
            defaults={"business_name": "Kariakoo Tech Hub", "region": "Dar es Salaam", "district": "Ilala"}
        )

    # ==========================================
    # STEP 3: AUTHENTICATION & USERS
    # ==========================================
    def test_01_registration(self):
        url = "/api/auth/register/"
        data = {
            "username": "new_user",
            "email": "newuser@example.com",
            "phone_number": "0745999888",
            "password": "SecurePassword999!",
            "role": "buyer"
        }
        res = self.client.post(url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", res.data)
        self.assertIn("access", res.data["tokens"])
        self.assertEqual(res.data["user"]["email"], "newuser@example.com")
        # Check normalized phone
        self.assertEqual(res.data["user"]["phone_number"], "+255745999888")

    def test_02_login_and_jwt(self):
        url = "/api/auth/login/"
        # Login via email
        res = self.client.post(url, {"email": "seller@kariakoo.tz", "password": "StrongPassword123!"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", res.data)
        access_token = res.data["tokens"]["access"]

        # Login via phone number
        res_phone = self.client.post(url, {"phone_number": "0712111222", "password": "StrongPassword123!"})
        self.assertEqual(res_phone.status_code, status.HTTP_200_OK)

        # Refresh token
        refresh_url = "/api/auth/token/refresh/"
        ref_res = self.client.post(refresh_url, {"refresh": res.data["tokens"]["refresh"]})
        self.assertEqual(ref_res.status_code, status.HTTP_200_OK)
        self.assertIn("access", ref_res.data)

    def test_03_phone_verification_otp(self):
        # 1. Request OTP
        req_res = self.client.post("/api/auth/request-phone-otp/", {"phone_number": "0768123456"})
        self.assertEqual(req_res.status_code, status.HTTP_200_OK)
        otp_code = req_res.data["dev_otp"]
        phone = req_res.data["phone_number"]

        # 2. Verify with wrong OTP fails
        fail_res = self.client.post("/api/auth/verify-phone/", {"phone_number": phone, "otp_code": "000000"})
        self.assertEqual(fail_res.status_code, status.HTTP_400_BAD_REQUEST)

        # 3. Verify with correct OTP succeeds
        self.client.force_authenticate(user=self.buyer)
        ok_res = self.client.post("/api/auth/verify-phone/", {"phone_number": phone, "otp_code": otp_code})
        self.assertEqual(ok_res.status_code, status.HTTP_200_OK)
        self.buyer.refresh_from_db()
        self.assertTrue(self.buyer.is_phone_verified)

    def test_04_user_me_profile_and_seller_profile(self):
        self.client.force_authenticate(user=self.seller)
        # GET
        res = self.client.get("/api/users/me/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["seller_profile"]["business_name"], "Kariakoo Tech Hub")

        # PATCH
        patch_res = self.client.patch("/api/users/me/", {
            "profile": {"bio": "Trusted tech electronics importer"},
            "seller_profile": {"tagline": "Best prices in Kariakoo"}
        }, format="json")
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data["profile"]["bio"], "Trusted tech electronics importer")
        self.assertEqual(patch_res.data["seller_profile"]["tagline"], "Best prices in Kariakoo")

    # ==========================================
    # STEP 4: LISTING ENGINE
    # ==========================================
    def test_05_listing_crud_and_owner_permissions(self):
        self.client.force_authenticate(user=self.seller)

        # Create Listing
        create_res = self.client.post("/api/listings/", {
            "title": "iPhone 14 Pro Max 256GB",
            "description": "Deep Purple, clean condition with box and accessories.",
            "price": "2100000.00",
            "category": self.cat_phones.id,
            "subcategory": self.sub_iphones.id,
            "condition": "LIKE_NEW",
            "region": "Dar es Salaam",
            "district": "Ilala",
            "attributes_data": [
                {"name": "Color", "value": "Deep Purple"},
                {"name": "Storage", "value": "256GB"}
            ]
        }, format="json")
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        listing_id = create_res.data["id"]

        # Intruder attempts to edit listing -> Forbidden (403)
        self.client.force_authenticate(user=self.intruder)
        hack_res = self.client.patch(f"/api/listings/{listing_id}/", {"price": "100.00"})
        self.assertEqual(hack_res.status_code, status.HTTP_403_FORBIDDEN)

        # Owner edits listing -> OK
        self.client.force_authenticate(user=self.seller)
        edit_res = self.client.patch(f"/api/listings/{listing_id}/", {"price": "2050000.00"})
        self.assertEqual(edit_res.status_code, status.HTTP_200_OK)
        self.assertEqual(edit_res.data["price"], "2050000.00")

        # Soft Delete listing
        del_res = self.client.delete(f"/api/listings/{listing_id}/")
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)

        # Check that deleted listing no longer appears in public active listing feed
        self.client.logout()
        pub_res = self.client.get("/api/listings/")
        ids = [item["id"] for item in extract_results(pub_res.data)]
        self.assertNotIn(listing_id, ids)

    # ==========================================
    # STEP 5: SEARCH AND FILTERING
    # ==========================================
    def test_06_search_and_filtering(self):
        # Create active test listings
        l1 = Listing.objects.create(
            seller=self.seller,
            category=self.cat_phones,
            title="Apple iPhone 12 Mini",
            description="Good battery life, clean screen",
            price=Decimal("750000.00"),
            region="Dar es Salaam",
            district="Ilala",
            condition="GOOD",
            status=Listing.STATUS_ACTIVE
        )
        l2 = Listing.objects.create(
            seller=self.seller,
            category=self.cat_phones,
            title="Samsung Galaxy S22",
            description="Phantom Black, Dual SIM",
            price=Decimal("1100000.00"),
            region="Mbeya",
            district="Mbeya Mjini",
            condition="LIKE_NEW",
            status=Listing.STATUS_ACTIVE
        )
        l3 = Listing.objects.create(
            seller=self.seller,
            category=self.cat_vehicles,
            title="Toyota RAV4 2018",
            description="Automatic, 4WD",
            price=Decimal("38000000.00"),
            region="Mbeya",
            district="Mbeya Mjini",
            condition="LIKE_NEW",
            status=Listing.STATUS_ACTIVE
        )

        # Search by keyword
        res_search = self.client.get("/api/listings/?search=iphone")
        results = extract_results(res_search.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], l1.id)

        # Filter by category slug
        res_cat = self.client.get("/api/listings/?category=phones")
        results_cat = extract_results(res_cat.data)
        self.assertEqual(len(results_cat), 2)

        # Filter by region
        res_region = self.client.get("/api/listings/?region=Mbeya")
        results_region = extract_results(res_region.data)
        self.assertEqual(len(results_region), 2)

        # Filter by price range
        res_price = self.client.get("/api/listings/?min_price=1000000&max_price=2000000")
        results_price = extract_results(res_price.data)
        self.assertEqual(len(results_price), 1)
        self.assertEqual(results_price[0]["id"], l2.id)

        # Sort by price ascending
        res_sort = self.client.get("/api/listings/?ordering=price")
        results_sort = extract_results(res_sort.data)
        self.assertEqual(results_sort[0]["id"], l1.id)

    # ==========================================
    # STEP 6: MESSAGING & FRAUD PREVENTION
    # ==========================================
    def test_07_messaging_engine(self):
        listing = Listing.objects.create(
            seller=self.seller,
            category=self.cat_phones,
            title="Google Pixel 7 Pro",
            description="Hazel color 128GB",
            price=Decimal("980000.00"),
            region="Dar es Salaam",
            district="Kinondoni",
            status=Listing.STATUS_ACTIVE
        )

        # Rule: User cannot message themselves on their own listing
        self.client.force_authenticate(user=self.seller)
        self_res = self.client.post("/api/conversations/", {
            "listing_id": listing.id,
            "initial_message": "Hello self"
        })
        self.assertEqual(self_res.status_code, status.HTTP_400_BAD_REQUEST)

        # Buyer starts conversation
        self.client.force_authenticate(user=self.buyer)
        start_res = self.client.post("/api/conversations/", {
            "listing_id": listing.id,
            "initial_message": "Habari, bei ya mwisho ni ngapi?"
        })
        self.assertEqual(start_res.status_code, status.HTTP_201_CREATED)
        conv_id = start_res.data["id"]

        # Intruder cannot read conversation messages (403)
        self.client.force_authenticate(user=self.intruder)
        peek_res = self.client.get(f"/api/conversations/{conv_id}/messages/")
        self.assertEqual(peek_res.status_code, status.HTTP_403_FORBIDDEN)

        # Seller reads messages -> automatically marks as read
        self.client.force_authenticate(user=self.seller)
        seller_read_res = self.client.get(f"/api/conversations/{conv_id}/messages/")
        self.assertEqual(seller_read_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(seller_read_res.data), 1)

        # Seller replies
        reply_res = self.client.post(f"/api/conversations/{conv_id}/messages/", {
            "content": "Habari, mwisho ni 950,000 TSh unakaribishwa dukani."
        })
        self.assertEqual(reply_res.status_code, status.HTTP_201_CREATED)

        # Buyer blocks conversation
        self.client.force_authenticate(user=self.buyer)
        block_res = self.client.post(f"/api/conversations/{conv_id}/block/")
        self.assertEqual(block_res.status_code, status.HTTP_200_OK)

        # Sending in blocked conversation is forbidden (403)
        blocked_msg_res = self.client.post(f"/api/conversations/{conv_id}/messages/", {
            "content": "Can I still reply?"
        })
        self.assertEqual(blocked_msg_res.status_code, status.HTTP_403_FORBIDDEN)

    # ==========================================
    # FAVORITES
    # ==========================================
    def test_08_favorites_workflow(self):
        listing = Listing.objects.create(
            seller=self.seller,
            category=self.cat_phones,
            title="MacBook Air M2",
            description="Midnight 512GB",
            price=Decimal("2800000.00"),
            region="Dar es Salaam",
            status=Listing.STATUS_ACTIVE
        )

        self.client.force_authenticate(user=self.buyer)
        # Add to favorites
        fav_res = self.client.post("/api/favorites/", {"listing_id": listing.id})
        self.assertEqual(fav_res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(fav_res.data["favorited"])

        # View favorites list
        list_res = self.client.get("/api/favorites/")
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data), 1)

        # Toggle to remove
        unfav_res = self.client.post("/api/favorites/", {"listing_id": listing.id})
        self.assertEqual(unfav_res.status_code, status.HTTP_200_OK)
        self.assertFalse(unfav_res.data["favorited"])
