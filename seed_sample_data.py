import os
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.marketplace.categories.models import Category, Subcategory
from apps.marketplace.listings.models import Listing, ListingAttribute, ListingImage

User = get_user_model()
seller, _ = User.objects.get_or_create(
    email="seller@atrium.market",
    defaults={
        "username": "lumina_tech",
        "name": "Lumina Luxury Tech & Goods",
        "phone_number": "+255755123456",
    },
)
if not seller.password:
    seller.set_password("Password123!")
    seller.save()

cat_elec = Category.objects.get(slug="electronics")
cat_lux = Category.objects.get(slug="luxury-fashion")
cat_auto = Category.objects.get(slug="automotive")
cat_prop = Category.objects.get(slug="real-estate")
cat_serv = Category.objects.get(slug="services")

listings_sample = [
    {
        "title": "MacBook Pro 16 M3 Max (64GB RAM / 2TB SSD) Space Black",
        "category": cat_elec,
        "description": "Pristine condition flagship Apple MacBook Pro M3 Max. Liquid Retina XDR display, 16-core CPU, 40-core GPU. Complete with original MagSafe charger, braided cable, and AppleCare+ warranty until late 2026. Perfect for AI engineering and 8K video pipelines.",
        "price": Decimal("7850000.00"),
        "condition": "LIKE_NEW",
        "region": "Dar es Salaam",
        "district": "Kinondoni",
        "ward": "Masaki",
        "is_negotiable": True,
        "attrs": [
            ("Processor", "Apple M3 Max 16-Core"),
            ("RAM", "64GB Unified Memory"),
            ("Storage", "2TB PCIe SSD"),
            ("Color", "Space Black"),
            ("Battery Health", "99%"),
        ],
    },
    {
        "title": "Rolex Submariner Date 41mm Kermit Oystersteel (Ref. 126610LV)",
        "category": cat_lux,
        "description": "Original Rolex Submariner Date 41mm green Cerachrom bezel with black dial. Complete with original presentation green box, chronometer certificate card, tags, and extra links. Verified authentic with papers. Available for in-person jeweler escrow in Dar es Salaam.",
        "price": Decimal("38500000.00"),
        "condition": "NEW",
        "region": "Dar es Salaam",
        "district": "Kinondoni",
        "ward": "Oysterbay",
        "is_negotiable": False,
        "attrs": [
            ("Brand", "Rolex"),
            ("Model", "Submariner Date 126610LV"),
            ("Case Size", "41mm"),
            ("Material", "Oystersteel"),
            ("Bezel", "Green Cerachrom"),
        ],
    },
    {
        "title": "Sony Alpha A7R V Full-Frame Mirrorless Camera + GM 24-70mm f/2.8 II",
        "category": cat_elec,
        "description": "61.0 MP full-frame Exmor R BSI CMOS sensor with dedicated AI processing unit. Exceptional autofocus tracking, 8K video recording, and 8-stop image stabilization. Bundled with Sony FE 24-70mm F2.8 GM II lens and dual Lexar CFexpress Type A cards.",
        "price": Decimal("11200000.00"),
        "condition": "LIKE_NEW",
        "region": "Dar es Salaam",
        "district": "Ilala",
        "ward": "Kariakoo",
        "is_negotiable": True,
        "attrs": [
            ("Sensor", "61MP Full-Frame"),
            ("Lens Included", "FE 24-70mm f/2.8 GM II"),
            ("Video", "8K 24p / 4K 60p"),
            ("Shutter Count", "3,200"),
        ],
    },
    {
        "title": "Range Rover Autobiography P530 V8 Long Wheelbase (2023)",
        "category": cat_auto,
        "description": "Santorini Black with Perlino Semi-Aniline executive rear leather seating. Twin-turbocharged 4.4L V8 engine generating 523 HP. Meridian Signature 1600W Sound System, active noise cancellation, rear-wheel steering, and air suspension. Clean local registration with low mileage.",
        "price": Decimal("520000000.00"),
        "condition": "LIKE_NEW",
        "region": "Dar es Salaam",
        "district": "Kinondoni",
        "ward": "Masaki",
        "is_negotiable": True,
        "attrs": [
            ("Make", "Land Rover Range Rover"),
            ("Year", "2023"),
            ("Engine", "4.4L Twin-Turbo V8"),
            ("Mileage", "14,200 km"),
            ("Transmission", "8-Speed Automatic"),
        ],
    },
    {
        "title": "Executive Waterfront Penthouse - 4 Bedroom with Ocean Terrace",
        "category": cat_prop,
        "description": "Panoramic Indian Ocean horizon views. 480 sq meters of architectural luxury with double-height ceiling living salon, Poggenpohl kitchen with Miele appliances, private plunge pool on terrace, and 24/7 biometric security with 3 underground parking slots.",
        "price": Decimal("1450000000.00"),
        "condition": "NEW",
        "region": "Dar es Salaam",
        "district": "Kinondoni",
        "ward": "Msasani",
        "is_negotiable": True,
        "attrs": [
            ("Property Type", "Penthouse / Luxury Flat"),
            ("Bedrooms", "4 Ensuite"),
            ("Bathrooms", "5"),
            ("Floor Area", "480 m2"),
            ("View", "Direct Oceanfront"),
        ],
    },
    {
        "title": "Enterprise Cloud Architecture and High-Scale Design Advisory",
        "category": cat_serv,
        "description": "Comprehensive fractional CTO and principal cloud architect advisory for fintechs, marketplaces, and high-concurrency systems. Architecture reviews, SOC2/ISO compliance hardening, Kubernetes orchestration, and database scaling.",
        "price": Decimal("9500000.00"),
        "condition": "NEW",
        "region": "Dar es Salaam",
        "district": "Ilala",
        "ward": "Posta / Kisutu",
        "is_negotiable": False,
        "attrs": [
            ("Service Type", "Software Advisory and Architecture"),
            ("Delivery", "Remote and On-site"),
            ("Engagement", "Monthly Retainer"),
        ],
    },
]

for item in listings_sample:
    attrs = item.pop("attrs")
    lst, created = Listing.objects.get_or_create(
        title=item["title"],
        defaults={**item, "seller": seller, "status": "ACTIVE"},
    )
    for k, v in attrs:
        ListingAttribute.objects.get_or_create(
            listing=lst, name=k, defaults={"value": v}
        )

print(f"Total Listings now: {Listing.objects.count()}")
