import os
import io
import django
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from users.models import UserProfile, SellerProfile
from apps.marketplace.categories.models import Category, Subcategory
from apps.marketplace.listings.models import Listing, ListingAttribute, ListingImage, Order, OrderItem
from apps.marketplace.messaging.models import Conversation, Message

User = get_user_model()

print("==> Seeding Atrium Platform Core Data...")

# 1. Core Users
seller, _ = User.objects.get_or_create(
    email="seller@atrium.market",
    defaults={
        "username": "lumina_tech",
        "name": "Lumina Luxury Tech & Goods",
        "phone_number": "+255755123456",
        "role": User.ROLE_SELLER,
        "is_phone_verified": True,
        "is_email_verified": True,
    },
)
seller.role = User.ROLE_SELLER
seller.is_phone_verified = True
seller.set_password("Password123!")
seller.save()

SellerProfile.objects.get_or_create(
    user=seller,
    defaults={
        "business_name": "Lumina Luxury Tech & Goods",
        "tagline": "East Africa's Premier Executive Electronics & Luxury Consignment",
        "description": "Certified authentic luxury goods, flagship electronics, and prime real estate with verified escrow guarantees.",
        "business_phone": "+255755123456",
        "whatsapp_number": "+255755123456",
        "region": "Dar es Salaam",
        "district": "Kinondoni",
        "ward": "Masaki",
        "street_address": "Toure Drive, Plot 42",
        "verification_status": SellerProfile.VERIFICATION_VERIFIED,
        "rating": Decimal("4.98"),
        "reviews_count": 84,
        "is_trusted": True,
    }
)

buyer, _ = User.objects.get_or_create(
    email="buyer@atrium.market",
    defaults={
        "username": "juma_salim",
        "name": "Juma Salim",
        "phone_number": "+255712345678",
        "role": User.ROLE_BUYER,
        "is_phone_verified": True,
        "is_email_verified": True,
    },
)
buyer.role = User.ROLE_BUYER
buyer.is_phone_verified = True
buyer.set_password("Password123!")
buyer.save()

UserProfile.objects.get_or_create(
    user=buyer,
    defaults={
        "region": "Dar es Salaam",
        "district": "Ilala",
        "ward": "Upanga",
    }
)

# Admin user
admin_user, _ = User.objects.get_or_create(
    email="admin@atrium.market",
    defaults={
        "username": "admin",
        "name": "Atrium Executive Admin",
        "role": User.ROLE_ADMIN,
        "is_staff": True,
        "is_superuser": True,
    }
)
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.set_password("AdminPass123!")
admin_user.save()

# 2. Categories & Subcategories
categories_data = [
    {
        "name": "Electronics & Gadgets",
        "slug": "electronics",
        "description": "High-performance computing, flagship smartphones, and pro audio gear.",
        "icon": "smartphone",
        "display_order": 1,
        "subs": [
            ("Laptops & Workstations", "laptops"),
            ("Smartphones & Tablets", "smartphones"),
            ("Cameras & Optical Gear", "cameras"),
            ("Pro Audio & Monitors", "audio"),
        ]
    },
    {
        "name": "Luxury & Fashion",
        "slug": "luxury-fashion",
        "description": "Designer timepieces, bespoke apparel, leather goods, and fine jewelry.",
        "icon": "watch",
        "display_order": 2,
        "subs": [
            ("Swiss Timepieces", "watches"),
            ("Fine Jewelry", "jewelry"),
            ("Designer Leather", "leather"),
        ]
    },
    {
        "name": "Vehicles & Automotive",
        "slug": "automotive",
        "description": "Prestige SUVs, luxury sedans, electric vehicles, and verified classics.",
        "icon": "car",
        "display_order": 3,
        "subs": [
            ("Prestige SUVs", "suvs"),
            ("Executive Sedans", "sedans"),
            ("Sports & Performance", "sports"),
        ]
    },
    {
        "name": "Real Estate & Living",
        "slug": "real-estate",
        "description": "Prime residential penthouses, executive apartments, and architectural villas.",
        "icon": "home",
        "display_order": 4,
        "subs": [
            ("Waterfront Penthouses", "penthouses"),
            ("Architectural Villas", "villas"),
            ("Commercial Spaces", "commercial"),
        ]
    },
    {
        "name": "Services & Consultancies",
        "slug": "services",
        "description": "High-end product design, cloud architecture, and corporate advisory.",
        "icon": "briefcase",
        "display_order": 5,
        "subs": [
            ("Cloud Architecture", "cloud"),
            ("Executive Advisory", "advisory"),
            ("Product Engineering", "engineering"),
        ]
    },
]

cats_map = {}
for cdata in categories_data:
    subs = cdata.pop("subs")
    cat, _ = Category.objects.update_or_create(
        slug=cdata["slug"],
        defaults=cdata
    )
    cats_map[cdata["slug"]] = cat
    for sname, sslug in subs:
        Subcategory.objects.update_or_create(
            category=cat,
            slug=sslug,
            defaults={"name": sname, "display_order": 1}
        )

# Helper to create placeholder image
def create_sample_image(text, bg_color=(20, 24, 33), fg_color=(212, 175, 55)):
    img = Image.new("RGB", (1200, 900), color=bg_color)
    draw = ImageDraw.Draw(img)
    # Draw simple design frame
    draw.rectangle([30, 30, 1170, 870], outline=fg_color, width=4)
    draw.rectangle([45, 45, 1155, 855], outline=(40, 48, 65), width=2)
    # Draw label text
    draw.text((70, 100), "ATRIUM FINE TRADE", fill=fg_color)
    draw.text((70, 180), text[:40], fill=(240, 240, 240))
    if len(text) > 40:
        draw.text((70, 240), text[40:80], fill=(180, 180, 180))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return buffer.read()

# 3. Luxury Sample Listings
sample_listings = [
    {
        "title": "MacBook Pro 16 M3 Max (64GB RAM / 2TB SSD) Space Black",
        "slug": "macbook-pro-16-m3-max-space-black",
        "category": cats_map["electronics"],
        "description": "Pristine condition flagship Apple MacBook Pro M3 Max. Liquid Retina XDR display, 16-core CPU, 40-core GPU. Complete with original MagSafe charger, braided cable, and AppleCare+ warranty until late 2026. Perfect for AI engineering and 8K video pipelines.",
        "price": Decimal("7850000.00"),
        "condition": "LIKE_NEW",
        "region": "Dar es Salaam",
        "district": "Kinondoni",
        "ward": "Masaki",
        "is_negotiable": True,
        "views_count": 420,
        "attrs": [
            ("Processor", "Apple M3 Max 16-Core"),
            ("RAM", "64GB Unified Memory"),
            ("Storage", "2TB PCIe SSD"),
            ("Color", "Space Black"),
            ("Battery Health", "99%"),
            ("AppleCare+", "Active until Dec 2026"),
        ],
        "bg_color": (15, 20, 30),
    },
    {
        "title": "Rolex Submariner Date 41mm Kermit Oystersteel (Ref. 126610LV)",
        "slug": "rolex-submariner-date-41mm-kermit",
        "category": cats_map["luxury-fashion"],
        "description": "Original Rolex Submariner Date 41mm green Cerachrom bezel with black dial. Complete with original presentation green box, chronometer certificate card, tags, and extra links. Verified authentic with papers. Available for in-person jeweler escrow in Dar es Salaam.",
        "price": Decimal("38500000.00"),
        "condition": "NEW",
        "region": "Dar es Salaam",
        "district": "Kinondoni",
        "ward": "Oysterbay",
        "is_negotiable": False,
        "views_count": 890,
        "attrs": [
            ("Brand", "Rolex"),
            ("Model", "Submariner Date 126610LV"),
            ("Case Size", "41mm"),
            ("Material", "Oystersteel 904L"),
            ("Bezel", "Green Cerachrom"),
            ("Movement", "Rolex Calibre 3235"),
        ],
        "bg_color": (12, 28, 20),
    },
    {
        "title": "Sony Alpha A7R V Full-Frame Mirrorless Camera + GM 24-70mm f/2.8 II",
        "slug": "sony-alpha-a7r-v-gm-lens-bundle",
        "category": cats_map["electronics"],
        "description": "61.0 MP full-frame Exmor R BSI CMOS sensor with dedicated AI processing unit. Exceptional autofocus tracking, 8K video recording, and 8-stop image stabilization. Bundled with Sony FE 24-70mm F2.8 GM II lens and dual Lexar CFexpress Type A cards.",
        "price": Decimal("11200000.00"),
        "condition": "LIKE_NEW",
        "region": "Dar es Salaam",
        "district": "Ilala",
        "ward": "Kariakoo",
        "is_negotiable": True,
        "views_count": 310,
        "attrs": [
            ("Sensor", "61MP Full-Frame Exmor R"),
            ("Lens Included", "Sony FE 24-70mm F2.8 GM II"),
            ("Video Resolution", "8K 24p / 4K 60p 10-bit"),
            ("Shutter Count", "3,200 clicks"),
            ("Warranty", "Sony East Africa Validated"),
        ],
        "bg_color": (25, 20, 20),
    },
    {
        "title": "Range Rover Autobiography P530 V8 Long Wheelbase (2023)",
        "slug": "range-rover-autobiography-p530-v8-2023",
        "category": cats_map["automotive"],
        "description": "Santorini Black with Perlino Semi-Aniline executive rear leather seating. Twin-turbocharged 4.4L V8 engine generating 523 HP. Meridian Signature 1600W Sound System, active noise cancellation, rear-wheel steering, and air suspension. Clean local registration with low mileage.",
        "price": Decimal("520000000.00"),
        "condition": "LIKE_NEW",
        "region": "Dar es Salaam",
        "district": "Kinondoni",
        "ward": "Masaki",
        "is_negotiable": True,
        "views_count": 1450,
        "attrs": [
            ("Make", "Land Rover"),
            ("Model", "Range Rover Autobiography LWB"),
            ("Year", "2023"),
            ("Engine", "4.4L Twin-Turbo V8 (523 HP)"),
            ("Mileage", "14,200 km"),
            ("Registration", "Dar es Salaam (Private)"),
        ],
        "bg_color": (15, 15, 20),
    },
    {
        "title": "Executive Waterfront Penthouse - 4 Bedroom with Ocean Terrace",
        "slug": "executive-waterfront-penthouse-msasani",
        "category": cats_map["real-estate"],
        "description": "Panoramic Indian Ocean horizon views. 480 sq meters of architectural luxury with double-height ceiling living salon, Poggenpohl kitchen with Miele appliances, private plunge pool on terrace, and 24/7 biometric security with 3 underground parking slots.",
        "price": Decimal("1450000000.00"),
        "condition": "NEW",
        "region": "Dar es Salaam",
        "district": "Kinondoni",
        "ward": "Msasani",
        "is_negotiable": True,
        "views_count": 2100,
        "attrs": [
            ("Property Type", "Penthouse / Luxury Flat"),
            ("Bedrooms", "4 Ensuite"),
            ("Bathrooms", "5"),
            ("Floor Area", "480 m2"),
            ("View", "Direct Oceanfront"),
            ("Parking", "3 Reserved Underground Slots"),
        ],
        "bg_color": (10, 25, 30),
    },
    {
        "title": "Enterprise Cloud Architecture and High-Scale Design Advisory",
        "slug": "enterprise-cloud-architecture-design-advisory",
        "category": cats_map["services"],
        "description": "Comprehensive fractional CTO and principal cloud architect advisory for fintechs, marketplaces, and high-concurrency systems. Architecture reviews, SOC2/ISO compliance hardening, Kubernetes orchestration, and database scaling.",
        "price": Decimal("9500000.00"),
        "condition": "NEW",
        "region": "Dar es Salaam",
        "district": "Ilala",
        "ward": "Posta / Kisutu",
        "is_negotiable": False,
        "views_count": 680,
        "attrs": [
            ("Service Type", "Software Advisory and Architecture"),
            ("Delivery", "Remote and On-site"),
            ("Engagement", "Monthly Retainer"),
            ("Certifications", "AWS Solutions Architect Pro & GCP Fellow"),
        ],
        "bg_color": (20, 20, 35),
    },
]

created_listings = []
for item in sample_listings:
    attrs = item.pop("attrs")
    bg = item.pop("bg_color")
    slug = item["slug"]
    
    lst, created = Listing.objects.update_or_create(
        slug=slug,
        defaults={
            **item,
            "seller": seller,
            "status": Listing.STATUS_ACTIVE,
        }
    )
    created_listings.append(lst)

    # Attributes
    lst.attributes.all().delete()
    for k, v in attrs:
        ListingAttribute.objects.create(listing=lst, name=k, value=v)

    # Images
    if not lst.images.exists():
        img_bytes = create_sample_image(lst.title, bg_color=bg)
        image_name = f"{lst.slug}.jpg"
        ListingImage.objects.create(
            listing=lst,
            image=ContentFile(img_bytes, name=image_name),
            is_primary=True,
            order=0
        )
    print(f"Listing '{lst.title}' (slug: {lst.slug}) seeded with image and attributes.")

# 4. Sample Conversation between buyer and seller
macbook_listing = created_listings[0]
conv, conv_created = Conversation.objects.get_or_create(
    listing=macbook_listing,
    buyer=buyer,
    defaults={"seller": seller}
)
if conv_created or not conv.messages.exists():
    Message.objects.create(
        conversation=conv,
        sender=buyer,
        content="Habari! Is the MacBook Pro 16 M3 Max still available in Masaki for inspection?"
    )
    Message.objects.create(
        conversation=conv,
        sender=seller,
        content="Hello Juma! Yes, it is in pristine condition with box, charger, and valid AppleCare+ warranty until late 2026. Available at Toure Drive."
    )
    Message.objects.create(
        conversation=conv,
        sender=buyer,
        content="Excellent. Would you accept an escrow offer of 7,300,000 TSh if I pick it up this afternoon?"
    )
print("Sample conversation between Buyer and Seller created.")

# 5. Sample Order
sample_order_num = "AT-2026-001"
order, ord_created = Order.objects.get_or_create(
    order_number=sample_order_num,
    defaults={
        "buyer": buyer,
        "buyer_name": "Juma Salim",
        "buyer_phone": "+255712345678",
        "buyer_email": "buyer@atrium.market",
        "delivery_method": Order.DELIVERY_COURIER,
        "delivery_district": "Ilala",
        "delivery_region": "Dar es Salaam",
        "delivery_address": "Upanga East, Ali Hassan Mwinyi Rd",
        "payment_method": Order.PAYMENT_MPESA,
        "status": Order.STATUS_ESCROW_LOCKED,
        "items_total": Decimal("7850000.00"),
        "delivery_fee": Decimal("15000.00"),
        "total_amount": Decimal("7865000.00"),
        "notes": "Handle with care, call recipient upon arrival at gate.",
    }
)
if ord_created or not order.items.exists():
    OrderItem.objects.create(
        order=order,
        listing=macbook_listing,
        title=macbook_listing.title,
        unit_price=macbook_listing.price,
        quantity=1
    )
print(f"Sample order {order.order_number} created.")

print("==> Database seeding complete! All core models are populated and ready.")
