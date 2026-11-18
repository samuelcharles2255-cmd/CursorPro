from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.marketplace.models import (
    DarLocation, Category, DAR_DISTRICT_CHOICES, DAR_WARDS_BY_DISTRICT
)


class Command(BaseCommand):
    help = "Seeds Dar es Salaam wards and standard Tanzanian marketplace categories"

    def handle(self, *args, **options):
        self.stdout.write("Seeding Dar es Salaam locations...")
        total_wards = 0
        commercial_hubs = ["Kariakoo", "Posta / Kisutu", "Sinza", "Mwenge", "Masaki", "Mikocheni", "Mbagala", "Ubungo"]

        for district, wards in DAR_WARDS_BY_DISTRICT.items():
            for ward in wards:
                is_hub = ward in commercial_hubs
                _, created = DarLocation.objects.get_or_create(
                    district=district,
                    ward_name=ward,
                    defaults={"is_commercial_hub": is_hub}
                )
                if created:
                    total_wards += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {total_wards} new Dar es Salaam wards."))

        self.stdout.write("Seeding categories with attribute schemas...")
        categories_data = [
            {
                "name_en": "Electronics & Gadgets",
                "name_sw": "Vifaa vya Kielektroniki",
                "icon": "smartphone",
                "display_order": 1,
                "is_featured": True,
                "subcategories": [
                    {
                        "name_en": "Smartphones & Tablets",
                        "name_sw": "Simu na Vishikwambi",
                        "icon": "smartphone",
                        "attribute_schema": [
                            {"key": "brand", "label_en": "Brand", "label_sw": "Chapa", "type": "select", "options": ["Apple", "Samsung", "Xiaomi", "Tecno", "Infinix", "Oppo", "Huawei", "Pixel", "Other"]},
                            {"key": "storage", "label_en": "Storage Capacity", "label_sw": "Ukubwa wa Kumbukumbu", "type": "select", "options": ["32GB", "64GB", "128GB", "256GB", "512GB", "1TB"]},
                            {"key": "ram", "label_en": "RAM", "label_sw": "RAM", "type": "select", "options": ["3GB", "4GB", "6GB", "8GB", "12GB", "16GB"]},
                            {"key": "battery_health", "label_en": "Battery Health (%)", "label_sw": "Afya ya Betri (%)", "type": "text"},
                        ]
                    },
                    {
                        "name_en": "Laptops & Computers",
                        "name_sw": "Kompyuta na Laptops",
                        "icon": "laptop",
                        "attribute_schema": [
                            {"key": "brand", "label_en": "Brand", "label_sw": "Chapa", "type": "select", "options": ["HP", "Dell", "Lenovo", "Apple (MacBook)", "Asus", "Acer", "Toshiba", "Other"]},
                            {"key": "processor", "label_en": "Processor", "label_sw": "Kichakataji (CPU)", "type": "select", "options": ["Core i3", "Core i5", "Core i7", "Core i9", "Apple M1", "Apple M2", "Apple M3", "AMD Ryzen 5", "AMD Ryzen 7"]},
                            {"key": "storage_type", "label_en": "Storage Type", "label_sw": "Aina ya Disk", "type": "select", "options": ["SSD", "HDD", "SSD + HDD"]},
                        ]
                    },
                    {
                        "name_en": "TVs, Audio & Home Cinema",
                        "name_sw": "Runinga na Mifumo ya Muziki",
                        "icon": "tv",
                        "attribute_schema": [
                            {"key": "screen_size", "label_en": "Screen Size (Inches)", "label_sw": "Ukubwa wa Skrini", "type": "select", "options": ["32\"", "40\"", "43\"", "50\"", "55\"", "65\"", "75\"+"]},
                            {"key": "is_smart_tv", "label_en": "Smart TV", "label_sw": "Smart TV", "type": "select", "options": ["Yes / Ndiyo", "No / Hapana"]},
                        ]
                    }
                ]
            },
            {
                "name_en": "Vehicles & Transport",
                "name_sw": "Magari na Usafiri",
                "icon": "car",
                "display_order": 2,
                "is_featured": True,
                "subcategories": [
                    {
                        "name_en": "Cars for Sale",
                        "name_sw": "Magari ya Kuuza",
                        "icon": "car",
                        "attribute_schema": [
                            {"key": "make", "label_en": "Make", "label_sw": "Kampuni", "type": "select", "options": ["Toyota", "Nissan", "Subaru", "Mercedes-Benz", "Suzuki", "Honda", "BMW", "Ford", "Other"]},
                            {"key": "year", "label_en": "Year of Manufacture", "label_sw": "Mwaka wa Kutengenezwa", "type": "text"},
                            {"key": "transmission", "label_en": "Transmission", "label_sw": "Mfumo wa Gia", "type": "select", "options": ["Automatic / Aina ya Auto", "Manual / Ya Mkono"]},
                            {"key": "fuel_type", "label_en": "Fuel Type", "label_sw": "Aina ya Mafuta", "type": "select", "options": ["Petrol", "Diesel", "Hybrid", "Electric"]},
                        ]
                    },
                    {
                        "name_en": "Motorcycles, Bodaboda & Bajaj",
                        "name_sw": "Pikipiki, Bodaboda na Bajaj",
                        "icon": "bike",
                        "attribute_schema": [
                            {"key": "vehicle_type", "label_en": "Vehicle Type", "label_sw": "Aina", "type": "select", "options": ["Bodaboda (Pikipiki)", "Bajaj (TVS/Piaggio)", "Scooter"]},
                            {"key": "brand", "label_en": "Brand", "label_sw": "Chapa", "type": "select", "options": ["Boxer", "TVS", "Haojue", "Yamaha", "Piaggio", "SanLG"]},
                        ]
                    }
                ]
            },
            {
                "name_en": "Fashion, Shoes & Clothing",
                "name_sw": "Mavazi, Viatu na Urembo",
                "icon": "shopping-bag",
                "display_order": 3,
                "is_featured": True,
                "subcategories": [
                    {
                        "name_en": "Men's Clothing & Footwear",
                        "name_sw": "Nguo na Viatu vya Wanaume",
                        "icon": "user",
                        "attribute_schema": [
                            {"key": "size", "label_en": "Size", "label_sw": "Saizi", "type": "text"},
                            {"key": "material", "label_en": "Material", "label_sw": "Kitambaa / Malighafi", "type": "text"},
                        ]
                    },
                    {
                        "name_en": "Women's Clothing & Handbags",
                        "name_sw": "Nguo, Mikoba na Viatu vya Wanawake",
                        "icon": "heart",
                        "attribute_schema": [
                            {"key": "size", "label_en": "Size", "label_sw": "Saizi", "type": "text"},
                        ]
                    }
                ]
            },
            {
                "name_en": "Home, Furniture & Appliances",
                "name_sw": "Vifaa vya Nyumbani na Samani",
                "icon": "home",
                "display_order": 4,
                "is_featured": True,
                "subcategories": [
                    {
                        "name_en": "Living Room & Bedroom Furniture",
                        "name_sw": "Samani za Sebule na Chumba",
                        "icon": "sofa",
                        "attribute_schema": [
                            {"key": "material", "label_en": "Material", "label_sw": "Aina ya Mbao/Kitambaa", "type": "text"},
                        ]
                    },
                    {
                        "name_en": "Kitchen Appliances & Fridges",
                        "name_sw": "Vifaa vya Jikoni na Majokofu",
                        "icon": "refrigerator",
                        "attribute_schema": [
                            {"key": "brand", "label_en": "Brand", "label_sw": "Chapa", "type": "text"},
                        ]
                    }
                ]
            },
            {
                "name_en": "Real Estate / Properties",
                "name_sw": "Nyumba, Viwanja na Fremu",
                "icon": "building",
                "display_order": 5,
                "is_featured": True,
                "subcategories": [
                    {
                        "name_en": "Houses & Apartments for Rent",
                        "name_sw": "Nyumba na Vyumba vya Kupanga",
                        "icon": "key",
                        "attribute_schema": [
                            {"key": "bedrooms", "label_en": "Bedrooms", "label_sw": "Idadi ya Vyumba vya Kulala", "type": "select", "options": ["Single Room", "1 Bedroom", "2 Bedrooms", "3 Bedrooms", "4+ Bedrooms"]},
                            {"key": "payment_terms", "label_en": "Rent Terms", "label_sw": "Masharti ya Kodi", "type": "select", "options": ["Mwezi 1", "Miezi 3", "Miezi 6", "Mwaka 1"]},
                            {"key": "master_bedroom", "label_en": "Master Bedroom", "label_sw": "Ina Master?", "type": "select", "options": ["Yes / Ndiyo", "No / Hapana"]},
                        ]
                    },
                    {
                        "name_en": "Commercial Shops & Frames",
                        "name_sw": "Fremu za Biashara na Ofisi",
                        "icon": "store",
                        "attribute_schema": [
                            {"key": "floor_level", "label_en": "Floor", "label_sw": "Ghorofa ya", "type": "text"},
                        ]
                    }
                ]
            },
            {
                "name_en": "Food, Groceries & Agriculture",
                "name_sw": "Vyakula na Kilimo",
                "icon": "coffee",
                "display_order": 6,
                "is_featured": False,
                "subcategories": []
            },
            {
                "name_en": "Services & Technicians",
                "name_sw": "Huduma na Mafundi",
                "icon": "wrench",
                "display_order": 7,
                "is_featured": False,
                "subcategories": []
            }
        ]

        created_cat_count = 0
        for top in categories_data:
            slug = slugify(top["name_en"])
            parent_cat, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name_en": top["name_en"],
                    "name_sw": top["name_sw"],
                    "icon": top.get("icon", "tag"),
                    "display_order": top.get("display_order", 0),
                    "is_featured": top.get("is_featured", False),
                }
            )
            created_cat_count += 1

            for sub in top.get("subcategories", []):
                sub_slug = slugify(f"{top['name_en']}-{sub['name_en']}")
                Category.objects.update_or_create(
                    slug=sub_slug,
                    defaults={
                        "parent": parent_cat,
                        "name_en": sub["name_en"],
                        "name_sw": sub["name_sw"],
                        "icon": sub.get("icon", "tag"),
                        "attribute_schema": sub.get("attribute_schema", []),
                    }
                )
                created_cat_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created_cat_count} categories and subcategories."))

        # Professional Verified Businesses & Listings
        from django.contrib.auth import get_user_model
        from apps.marketplace.models import BusinessProfile, Listing
        from decimal import Decimal

        User = get_user_model()
        merchant_user, _ = User.objects.get_or_create(
            username="apex_electronics",
            defaults={"email": "contact@apexelectronics.co.tz", "name": "Rashid Mwinyi", "role": "employer"}
        )

        biz, _ = BusinessProfile.objects.update_or_create(
            user=merchant_user,
            defaults={
                "business_name": "Apex Electronics Ltd",
                "tagline": "Premium Consumer Electronics & Computing Hardware",
                "description": "Authorized dealer of smartphones, computing systems, and professional workstation hardware in Dar es Salaam. All products include official warranty documentation and fiscal EFD receipts.",
                "phone_number": "+255712000111",
                "whatsapp_number": "+255712000111",
                "district": "ilala",
                "ward": "Kariakoo",
                "street_address": "Kongo & Aggrey Commercial Center, 1st Floor",
                "landmark_directions": "Opposite NMB Bank, Clock Tower Plaza, Suite 14.",
                "google_maps_url": "https://maps.google.com/?q=Kariakoo+Dar+es+Salaam",
                "verification_status": BusinessProfile.VERIFICATION_VERIFIED,
                "total_views": 1420,
                "total_contacts": 89
            }
        )

        biz2_user, _ = User.objects.get_or_create(
            username="nordic_motors",
            defaults={"email": "sales@nordicmotors.co.tz", "name": "Juma Simba", "role": "employer"}
        )

        biz2, _ = BusinessProfile.objects.update_or_create(
            user=biz2_user,
            defaults={
                "business_name": "Nordic Motors Tanzania",
                "tagline": "Quality Pre-Owned & Brand New Motor Vehicles",
                "description": "Direct vehicle importer specializing in Japanese and European motor vehicles. Comprehensive pre-delivery inspection, TRA clearance, and warranty coverage provided.",
                "phone_number": "+255754999888",
                "whatsapp_number": "+255754999888",
                "district": "kinondoni",
                "ward": "Sinza",
                "street_address": "Sinza Mori Commercial Belt",
                "landmark_directions": "Adjacent to Puma Energy Station, Main Yard.",
                "verification_status": BusinessProfile.VERIFICATION_VERIFIED,
                "total_views": 850,
                "total_contacts": 45
            }
        )

        phone_cat = Category.objects.filter(slug__icontains="smart").first() or Category.objects.first()
        laptop_cat = Category.objects.filter(slug__icontains="laptop").first() or phone_cat
        car_cat = Category.objects.filter(slug__icontains="car").first() or phone_cat

        # Remove previous informal listings
        Listing.objects.filter(title__icontains="Mtumba").delete()

        demo_listings = [
            {
                "seller": biz,
                "category": phone_cat,
                "title": "Apple iPhone 15 Pro Max 256GB - Natural Titanium (Certified)",
                "description": "Apple iPhone 15 Pro Max 256GB in pristine condition. Battery health 98%, complete with original box, documentation, and accessories. 6 months warranty included.",
                "price": Decimal("2450000.00"),
                "is_negotiable": True,
                "condition": Listing.CONDITION_LIKE_NEW,
                "district": "ilala",
                "ward": "Kariakoo",
                "pickup_available": True,
                "delivery_available": True,
                "attributes": {"brand": "Apple", "storage": "256GB", "battery_health": "98%"}
            },
            {
                "seller": biz,
                "category": phone_cat,
                "title": "Samsung Galaxy S24 Ultra 512GB - Titanium Black (Brand New)",
                "description": "Brand new factory sealed unit. 12GB RAM, 512GB storage, 200MP AI camera system. Full manufacturer warranty and EFD fiscal receipt.",
                "price": Decimal("2850000.00"),
                "is_negotiable": False,
                "condition": Listing.CONDITION_NEW,
                "district": "ilala",
                "ward": "Kariakoo",
                "pickup_available": True,
                "delivery_available": True,
                "attributes": {"brand": "Samsung", "storage": "512GB", "ram": "12GB"}
            },
            {
                "seller": biz,
                "category": laptop_cat,
                "title": "Apple MacBook Pro 14\" M2 Pro (16GB RAM / 512GB SSD)",
                "description": "Space Gray finish, 10-core CPU, 16-core GPU, 16GB Unified Memory, 512GB high-speed SSD. Pristine condition with minimal battery cycles.",
                "price": Decimal("3400000.00"),
                "is_negotiable": True,
                "condition": Listing.CONDITION_LIKE_NEW,
                "district": "ilala",
                "ward": "Kariakoo",
                "pickup_available": True,
                "delivery_available": True,
                "attributes": {"brand": "Apple (MacBook)", "processor": "Apple M2 Pro", "storage_type": "SSD"}
            },
            {
                "seller": biz2,
                "category": car_cat,
                "title": "Toyota Harrier 2.0L Premium Package (2016, Automatic)",
                "description": "Black metallic exterior, black leather interior, panoramic glass sunroof, premium sound system, low certified mileage with full service history.",
                "price": Decimal("48500000.00"),
                "is_negotiable": True,
                "condition": Listing.CONDITION_GOOD,
                "district": "kinondoni",
                "ward": "Sinza",
                "pickup_available": True,
                "delivery_available": False,
                "attributes": {"make": "Toyota", "year": "2016", "transmission": "Automatic", "fuel_type": "Petrol"}
            }
        ]

        for item in demo_listings:
            Listing.objects.update_or_create(
                title=item["title"],
                defaults=item
            )

        # Remove old informal businesses if any
        BusinessProfile.objects.filter(business_name__in=["Kariakoo Smart Tech", "Sinza Auto Point"]).delete()

        self.stdout.write(self.style.SUCCESS("Seeded professional verified merchants and enterprise listings."))
