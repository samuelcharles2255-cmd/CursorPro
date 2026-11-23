from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from users.models import User as CustomUser, UserProfile, SellerProfile
from users.validators import validate_tz_phone, normalize_tz_phone
from apps.marketplace.categories.models import Category, Subcategory
from apps.marketplace.listings.models import Listing, ListingImage, ListingAttribute
from apps.marketplace.messaging.models import Conversation, Message
from apps.marketplace.favorites.models import Favorite

UserModel = get_user_model()


class TanzanianPhoneValidatorTests(TestCase):
    def test_normalization(self):
        self.assertEqual(normalize_tz_phone("0712345678"), "+255712345678")
        self.assertEqual(normalize_tz_phone("255712345678"), "+255712345678")
        self.assertEqual(normalize_tz_phone("+255 712 345 678"), "+255712345678")
        self.assertEqual(normalize_tz_phone("0682123456"), "+255682123456")

    def test_validation_valid_operators(self):
        # Vodacom (74, 75, 76)
        validate_tz_phone("0754123456")
        # Airtel (68, 69, 78)
        validate_tz_phone("+255682123456")
        # Tigo (65, 67, 71)
        validate_tz_phone("0713123456")
        # Halotel (61, 62)
        validate_tz_phone("0621123456")
        # TTCL (73)
        validate_tz_phone("0732123456")

    def test_validation_invalid_numbers(self):
        with self.assertRaises(ValidationError):
            validate_tz_phone("0123456789")  # Invalid country/prefix
        with self.assertRaises(ValidationError):
            validate_tz_phone("12345")  # Too short


class MainMarketplaceModelsTests(TestCase):
    def setUp(self):
        self.seller_user = UserModel.objects.create_user(
            username="seller_tz",
            email="seller@example.co.tz",
            password="StrongPassword123!"
        )
        self.buyer_user = UserModel.objects.create_user(
            username="buyer_tz",
            email="buyer@example.co.tz",
            password="StrongPassword123!"
        )

    def test_categories_and_subcategories(self):
        cat = Category.objects.create(name="Electronics", icon="smartphone")
        self.assertEqual(cat.slug, "electronics")

        sub = Subcategory.objects.create(category=cat, name="Smartphones")
        self.assertEqual(sub.slug, "smartphones")
        self.assertEqual(str(sub), "Electronics > Smartphones")

    def test_listing_engine_and_attributes(self):
        cat = Category.objects.create(name="Phones & Tablets")
        listing = Listing.objects.create(
            seller=self.seller_user,
            category=cat,
            title="iPhone 13 Pro 128GB",
            description="Clean condition, battery health 88%",
            price=Decimal("1350000.00"),
            region="Dar es Salaam",
            district="Kinondoni",
            condition=Listing.CONDITION_LIKE_NEW,
            status=Listing.STATUS_ACTIVE
        )
        self.assertTrue(listing.slug.startswith("iphone-13-pro-128gb"))
        self.assertTrue(listing.is_active)

        # Attribute
        attr = ListingAttribute.objects.create(
            listing=listing,
            name="Storage",
            value="128GB"
        )
        self.assertEqual(listing.attributes.count(), 1)

        # Soft delete
        listing.soft_delete()
        self.assertTrue(listing.is_deleted)
        self.assertFalse(listing.is_active)

    def test_messaging_rules(self):
        cat = Category.objects.create(name="Vehicles")
        listing = Listing.objects.create(
            seller=self.seller_user,
            category=cat,
            title="Toyota IST",
            description="Good runner",
            price=Decimal("9500000.00"),
            region="Mbeya",
            district="Mbeya Mjini"
        )

        # Self-messaging should raise ValidationError
        conv_self = Conversation(
            listing=listing,
            buyer=self.seller_user,
            seller=self.seller_user
        )
        with self.assertRaises(ValidationError):
            conv_self.clean()

        # Valid conversation
        conv = Conversation.objects.create(
            listing=listing,
            buyer=self.buyer_user,
            seller=self.seller_user
        )
        msg = Message.objects.create(
            conversation=conv,
            sender=self.buyer_user,
            content="Habari, je hii gari bado ipo?"
        )
        self.assertEqual(conv.messages.count(), 1)
        self.assertEqual(conv.last_message.content, "Habari, je hii gari bado ipo?")

    def test_favorite_uniqueness(self):
        cat = Category.objects.create(name="Fashion")
        listing = Listing.objects.create(
            seller=self.seller_user,
            category=cat,
            title="Sneakers",
            description="Size 42",
            price=Decimal("50000.00"),
            region="Arusha",
            district="Arusha Mjini"
        )
        fav = Favorite.objects.create(user=self.buyer_user, listing=listing)
        self.assertEqual(fav.listing, listing)
