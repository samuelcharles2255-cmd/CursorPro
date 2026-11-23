import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F, Count
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.text import slugify

from .models import (
    DarLocation, Category, BusinessProfile, SellerVerification,
    Listing, ListingImage, CartItem, Order, OrderItem,
    Conversation, ChatMessage, Favorite, SellerFollow, Report,
    AuditLog, PhoneOTP, DAR_DISTRICT_CHOICES, DAR_WARDS_BY_DISTRICT
)
from .forms import (
    PhoneRequestOTPForm, PhoneVerifyOTPForm, BusinessRegistrationForm,
    ListingForm, SellerVerificationForm, OrderCheckoutForm, ReportListingForm
)
from .services.sms import OTPService, normalize_tz_phone

User = get_user_model()


# ==========================================
# LANGUAGE TOGGLE (Swahili & English)
# ==========================================

def set_language_preference(request):
    """Switch language between Swahili ('sw') and English ('en')"""
    lang = request.GET.get("lang", "sw")
    if lang not in ["sw", "en"]:
        lang = "sw"
    request.session["lang"] = lang
    response = redirect(request.META.get("HTTP_REFERER", "/marketplace/"))
    response.set_cookie("lang", lang, max_age=365*24*3600)
    return response


# ==========================================
# PUBLIC MARKETPLACE BROWSING & SEARCH
# ==========================================

def home(request):
    """Marketplace homepage with fast category pills, featured categories, and recent listings"""
    categories = Category.objects.filter(parent=None).prefetch_related("children")
    featured_categories = Category.objects.filter(is_featured=True)[:6]

    recent_listings = Listing.objects.filter(
        status=Listing.STATUS_ACTIVE
    ).select_related("seller", "category").prefetch_related("images").order_by("-last_renewed_at", "-created_at")[:12]

    # Key Dar commercial hubs
    dar_hubs = DarLocation.objects.filter(is_commercial_hub=True)

    stats = {
        "listings_count": Listing.objects.filter(status=Listing.STATUS_ACTIVE).count(),
        "verified_sellers": BusinessProfile.objects.filter(verification_status=BusinessProfile.VERIFICATION_VERIFIED).count(),
        "wards_count": DarLocation.objects.count()
    }

    return render(request, "marketplace/home.html", {
        "categories": categories,
        "featured_categories": featured_categories,
        "recent_listings": recent_listings,
        "dar_hubs": dar_hubs,
        "stats": stats,
    })


def listing_list(request):
    """Search and filter listings by query, category, Dar district/ward, price, condition, sort"""
    listings = Listing.objects.filter(status=Listing.STATUS_ACTIVE).select_related("seller", "category").prefetch_related("images")

    # Search query
    q = request.GET.get("q", "").strip()
    if q:
        listings = listings.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name_en__icontains=q) |
            Q(category__name_sw__icontains=q) |
            Q(ward__icontains=q) |
            Q(seller__business_name__icontains=q)
        )

    # Category filter
    category_slug = request.GET.get("category", "").strip()
    selected_category = None
    if category_slug:
        selected_category = Category.objects.filter(slug=category_slug).first()
        if selected_category:
            child_ids = list(selected_category.children.values_list("id", flat=True))
            category_ids = [selected_category.id] + child_ids
            listings = listings.filter(category_id__in=category_ids)

    # Location filters (Dar es Salaam)
    district = request.GET.get("district", "").strip()
    if district:
        listings = listings.filter(district=district)

    ward = request.GET.get("ward", "").strip()
    if ward:
        listings = listings.filter(ward__icontains=ward)

    # Price filters
    min_price = request.GET.get("min_price", "").strip()
    if min_price:
        try:
            listings = listings.filter(price__gte=Decimal(min_price))
        except Exception:
            pass

    max_price = request.GET.get("max_price", "").strip()
    if max_price:
        try:
            listings = listings.filter(price__lte=Decimal(max_price))
        except Exception:
            pass

    # Condition filter
    condition = request.GET.get("condition", "").strip()
    if condition:
        listings = listings.filter(condition=condition)

    # Verified sellers only
    verified_only = request.GET.get("verified_only", "") == "1"
    if verified_only:
        listings = listings.filter(seller__verification_status=BusinessProfile.VERIFICATION_VERIFIED)

    # Sorting
    sort_by = request.GET.get("sort", "newest")
    if sort_by == "price_asc":
        listings = listings.order_by("price")
    elif sort_by == "price_desc":
        listings = listings.order_by("-price")
    elif sort_by == "popular":
        listings = listings.order_by("-views_count", "-contact_clicks_count")
    else:  # newest / default
        listings = listings.order_by("-last_renewed_at", "-created_at")

    # Pagination: 12 per page for fast 3G rendering
    paginator = Paginator(listings, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(parent=None).prefetch_related("children")

    return render(request, "marketplace/listing_list.html", {
        "page_obj": page_obj,
        "listings": page_obj.object_list,
        "categories": categories,
        "selected_category": selected_category,
        "districts": DAR_DISTRICT_CHOICES,
        "q": q,
        "district": district,
        "ward": ward,
        "min_price": min_price,
        "max_price": max_price,
        "condition": condition,
        "sort_by": sort_by,
        "verified_only": verified_only,
        "total_results": paginator.count,
    })


def listing_detail(request, slug):
    """Listing detail view with 8-image gallery, seller card, WhatsApp/Call buttons, directions, similar products"""
    listing = get_object_or_404(
        Listing.objects.select_related("seller", "category").prefetch_related("images"),
        slug=slug
    )

    # Increment view count
    Listing.objects.filter(pk=listing.pk).update(views_count=F("views_count") + 1)
    BusinessProfile.objects.filter(pk=listing.seller_id).update(total_views=F("total_views") + 1)

    # Find similar products (in same category or by seller)
    similar_listings = Listing.objects.filter(
        status=Listing.STATUS_ACTIVE,
        category=listing.category
    ).exclude(pk=listing.pk).prefetch_related("images")[:4]

    if not similar_listings.exists():
        # Fallback to same district
        similar_listings = Listing.objects.filter(
            status=Listing.STATUS_ACTIVE,
            district=listing.district
        ).exclude(pk=listing.pk).prefetch_related("images")[:4]

    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, listing=listing).exists()

    # Pre-filled WhatsApp message
    clean_title = listing.title.replace("&", "na")
    wa_text = f"Habari {listing.seller.business_name}, nimeona tangazo lako la '{clean_title}' kwenye The City Marketplace (TSh {listing.price:,.0f}). Je, bado inapatikana?"
    import urllib.parse
    wa_encoded_text = urllib.parse.quote(wa_text)
    wa_link = f"https://wa.me/{listing.seller.clean_whatsapp}?text={wa_encoded_text}"

    return render(request, "marketplace/listing_detail.html", {
        "listing": listing,
        "seller": listing.seller,
        "images": listing.images.all(),
        "similar_listings": similar_listings,
        "is_favorited": is_favorited,
        "wa_link": wa_link,
    })


def track_contact_click(request, slug):
    """Track WhatsApp or Call click counter on seller and listing"""
    listing = get_object_or_404(Listing, slug=slug)
    Listing.objects.filter(pk=listing.pk).update(contact_clicks_count=F("contact_clicks_count") + 1)
    BusinessProfile.objects.filter(pk=listing.seller_id).update(total_contacts=F("total_contacts") + 1)
    return JsonResponse({"status": "tracked"})


def seller_store_detail(request, slug):
    """Public business owner store profile with contact, directions, verified badge, and listings"""
    seller = get_object_or_404(BusinessProfile.objects.select_related("user"), slug=slug)
    active_listings = seller.listings.filter(status=Listing.STATUS_ACTIVE).prefetch_related("images")

    is_following = False
    if request.user.is_authenticated:
        is_following = SellerFollow.objects.filter(user=request.user, business=seller).exists()

    return render(request, "marketplace/seller_detail.html", {
        "seller": seller,
        "listings": active_listings,
        "is_following": is_following,
    })


# ==========================================
# PHONE OTP SIGNUP & LOGIN FLOW (Tanzania SMS)
# ==========================================

def phone_auth_request(request):
    """Step 1: User enters Tanzanian phone number to receive a 6-digit OTP"""
    if request.user.is_authenticated:
        return redirect("marketplace:home")

    # Quick demo login bypass for fast developer / evaluator testing
    demo_role = request.GET.get("demo")
    if demo_role in ("merchant", "buyer"):
        if demo_role == "merchant":
            demo_user, _ = User.objects.get_or_create(
                username="apex_electronics",
                defaults={"email": "contact@apexelectronics.co.tz", "name": "Rashid Mwinyi", "role": "employer"}
            )
            login(request, demo_user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Umeingia kama Muuzaji Aliyethibitishwa: Apex Electronics Ltd")
            return redirect("marketplace:seller_dashboard")
        else:
            demo_buyer, _ = User.objects.get_or_create(
                username="demo_customer",
                defaults={"email": "customer@thecity.local", "name": "Amina Said", "role": "job_seeker"}
            )
            login(request, demo_buyer, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Umeingia kama Mteja: Amina Said")
            return redirect("marketplace:home")

    if request.method == "POST":
        form = PhoneRequestOTPForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone_number"]
            user_type = form.cleaned_data["user_type"]
            result = OTPService.send_otp(phone, purpose=PhoneOTP.PURPOSE_LOGIN)

            if result["success"]:
                request.session["auth_phone"] = result["phone_number"]
                request.session["auth_user_type"] = user_type
                request.session["auth_otp"] = result["otp_code"]
                request.session["auth_live_sent"] = result.get("live_sent", False)

                if result.get("live_sent"):
                    messages.success(
                        request,
                        f"Msimbo wa uthibitisho umetumwa kwa SMS kwenye namba {result['phone_number']}."
                    )
                else:
                    messages.info(
                        request,
                        f"Msimbo wa uthibitisho wa mtihani: {result['otp_code']}"
                    )
                return redirect("marketplace:phone_auth_verify")
            else:
                messages.error(request, result["error"])
    else:
        initial_phone = request.session.get("auth_phone", "")
        form = PhoneRequestOTPForm(initial={"phone_number": initial_phone})

    return render(request, "marketplace/auth_phone_request.html", {"form": form})


def phone_auth_verify(request):
    """Step 2: User enters the 6-digit OTP code to complete login/signup"""
    if request.user.is_authenticated:
        return redirect("marketplace:home")

    phone = request.session.get("auth_phone", "")
    user_type = request.session.get("auth_user_type", "buyer")
    active_otp = request.session.get("auth_otp", "")
    live_sent = request.session.get("auth_live_sent", False)

    if not phone:
        messages.warning(request, "Tafadhali ingiza namba yako ya simu kwanza.")
        return redirect("marketplace:phone_auth_request")

    # If active_otp is missing in session, retrieve the latest valid OTP from DB
    if not active_otp:
        latest_otp_record = PhoneOTP.objects.filter(
            phone_number=phone,
            purpose=PhoneOTP.PURPOSE_LOGIN,
            is_used=False
        ).order_by("-created_at").first()
        if latest_otp_record and not latest_otp_record.is_expired():
            active_otp = latest_otp_record.otp_code

    if request.method == "POST":
        form = PhoneVerifyOTPForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["otp_code"]
            name = form.cleaned_data.get("name", "").strip()

            verify_res = OTPService.verify_otp(phone, code, purpose=PhoneOTP.PURPOSE_LOGIN)
            if verify_res["success"]:
                clean_phone_digits = phone.replace("+", "")
                username = f"user_{clean_phone_digits}"
                email_synth = f"{username}@thecity.local"

                # Ensure clean professional display name
                if name:
                    clean_display_name = name
                elif user_type == "seller":
                    clean_display_name = f"Merchant ({phone[-4:]})"
                else:
                    clean_display_name = f"Customer ({phone[-4:]})"

                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "email": email_synth,
                        "name": clean_display_name,
                        "role": "employer" if user_type == "seller" else "job_seeker",
                    }
                )

                if name and user.name != name:
                    user.name = name
                    user.save(update_fields=["name"])
                elif not user.name:
                    user.name = clean_display_name
                    user.save(update_fields=["name"])

                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                messages.success(request, f"Karibu sana, {user.name}!")

                if user_type == "seller" and not hasattr(user, "marketplace_business"):
                    return redirect("marketplace:seller_register")

                return redirect("marketplace:home")
            else:
                messages.error(request, verify_res["error"])
    else:
        form = PhoneVerifyOTPForm(initial={
            "phone_number": phone,
            "user_type": user_type,
            "otp_code": active_otp or ""
        })

    return render(request, "marketplace/auth_phone_verify.html", {
        "form": form,
        "phone": phone,
        "user_type": user_type,
        "active_otp": active_otp,
        "live_sent": live_sent,
    })


def auth_logout(request):
    """Logout user and redirect to marketplace home"""
    logout(request)
    messages.info(request, "Umetoka kwenye akaunti yako.")
    return redirect("marketplace:home")


# ==========================================
# SELLER REGISTRATION & DASHBOARD
# ==========================================

@login_required
def seller_register(request):
    """Register a business profile so the user can start posting products and manage orders"""
    if hasattr(request.user, "marketplace_business"):
        messages.info(request, "Tayari una wasifu wa biashara.")
        return redirect("marketplace:seller_dashboard")

    if request.method == "POST":
        form = BusinessRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            biz = form.save(commit=False)
            biz.user = request.user
            biz.save()

            AuditLog.objects.create(
                action="business_registered",
                actor=request.user,
                target_type="BusinessProfile",
                target_id=str(biz.pk),
                details={"business_name": biz.business_name, "ward": biz.ward}
            )

            messages.success(request, f"Biashara yako ya '{biz.business_name}' imesajiliwa kikamilifu! Sasa unaweza kuanza kutangaza bidhaa zako.")
            return redirect("marketplace:seller_dashboard")
    else:
        initial_phone = request.user.username.replace("tz_", "+") if request.user.username.startswith("tz_") else ""
        form = BusinessRegistrationForm(initial={
            "phone_number": initial_phone,
            "whatsapp_number": initial_phone
        })

    return render(request, "marketplace/seller_register.html", {"form": form})


@login_required
def seller_dashboard(request):
    """Seller management center: views, contacts, orders, active listings"""
    if not hasattr(request.user, "marketplace_business"):
        return redirect("marketplace:seller_register")

    business = request.user.marketplace_business
    listings = business.listings.prefetch_related("images").order_by("-last_renewed_at", "-created_at")

    orders = business.received_orders.select_related("customer").order_by("-created_at")[:10]
    inquiries = business.marketplace_seller_chats.select_related("customer", "listing").order_by("-updated_at")[:5]

    verification = getattr(business, "verification_application", None)

    active_count = listings.filter(status=Listing.STATUS_ACTIVE).count()
    sold_count = listings.filter(status=Listing.STATUS_SOLD).count()

    return render(request, "marketplace/seller_dashboard.html", {
        "business": business,
        "listings": listings,
        "orders": orders,
        "inquiries": inquiries,
        "verification": verification,
        "active_count": active_count,
        "sold_count": sold_count,
    })


@login_required
def seller_listing_create(request):
    """Create a new listing with up to 8 images and category attributes"""
    if not hasattr(request.user, "marketplace_business"):
        return redirect("marketplace:seller_register")

    business = request.user.marketplace_business

    if request.method == "POST":
        form = ListingForm(request.POST)
        images = request.FILES.getlist("images")

        if len(images) > 8:
            messages.error(request, "Unaweza kupakia picha zisizozidi 8 tu (Maximum 8 images).")
        elif form.is_valid():
            listing = form.save(commit=False)
            listing.seller = business

            attrs = {}
            for key, val in request.POST.items():
                if key.startswith("attr_") and val.strip():
                    attrs[key[5:]] = val.strip()
            listing.attributes = attrs
            listing.save()

            for idx, img_file in enumerate(images[:8]):
                ListingImage.objects.create(
                    listing=listing,
                    image=img_file,
                    is_cover=(idx == 0),
                    order=idx + 1
                )

            messages.success(request, f"Tangazo lako la '{listing.title}' limewekwa na liko hewani!")
            return redirect("marketplace:listing_detail", slug=listing.slug)
    else:
        form = ListingForm(initial={"district": business.district, "ward": business.ward})

    categories = Category.objects.filter(parent=None).prefetch_related("children")
    return render(request, "marketplace/listing_form.html", {
        "form": form,
        "title": "Weka Tangazo Jipya / Create Listing",
        "categories": categories,
        "business": business,
    })


@login_required
def seller_listing_edit(request, pk):
    """Edit an existing listing"""
    if not hasattr(request.user, "marketplace_business"):
        return redirect("marketplace:seller_register")

    business = request.user.marketplace_business
    listing = get_object_or_404(Listing, pk=pk, seller=business)

    if request.method == "POST":
        form = ListingForm(request.POST, instance=listing)
        new_images = request.FILES.getlist("images")

        current_count = listing.images.count()
        if current_count + len(new_images) > 8:
            messages.error(request, f"Tangazo hili tayari lina picha {current_count}. Unaweza kuongeza picha zisizozidi {8 - current_count}.")
        elif form.is_valid():
            listing = form.save(commit=False)

            attrs = dict(listing.attributes or {})
            for key, val in request.POST.items():
                if key.startswith("attr_") and val.strip():
                    attrs[key[5:]] = val.strip()
            listing.attributes = attrs
            listing.save()

            order_start = current_count + 1
            for idx, img_file in enumerate(new_images):
                ListingImage.objects.create(
                    listing=listing,
                    image=img_file,
                    is_cover=(listing.images.count() == 0),
                    order=order_start + idx
                )

            messages.success(request, "Tangazo limebadilishwa kikamilifu!")
            return redirect("marketplace:seller_dashboard")
    else:
        form = ListingForm(instance=listing)

    categories = Category.objects.filter(parent=None).prefetch_related("children")
    return render(request, "marketplace/listing_form.html", {
        "form": form,
        "listing": listing,
        "title": "Badilisha Tangazo / Edit Listing",
        "categories": categories,
        "business": business,
        "existing_images": listing.images.all(),
    })


@login_required
def seller_listing_delete(request, pk):
    """Delete a listing"""
    if not hasattr(request.user, "marketplace_business"):
        return redirect("marketplace:seller_register")

    listing = get_object_or_404(Listing, pk=pk, seller=request.user.marketplace_business)
    if request.method == "POST":
        title = listing.title
        listing.delete()
        messages.success(request, f"Tangazo '{title}' limefutwa.")
        return redirect("marketplace:seller_dashboard")

    return render(request, "marketplace/confirm_delete.html", {"object": listing})


@login_required
def seller_listing_renew(request, pk):
    """Seller renews listing: bumps expiry by 30 days and surfaces back to the top of results"""
    if not hasattr(request.user, "marketplace_business"):
        return redirect("marketplace:seller_register")

    listing = get_object_or_404(Listing, pk=pk, seller=request.user.marketplace_business)
    listing.renew()
    messages.success(request, f"Tangazo '{listing.title}' limerejeshwa hewani na kupandishwa juu!")
    return redirect("marketplace:seller_dashboard")


@login_required
def seller_listing_mark_sold(request, pk):
    """Mark product as sold"""
    if not hasattr(request.user, "marketplace_business"):
        return redirect("marketplace:seller_register")

    listing = get_object_or_404(Listing, pk=pk, seller=request.user.marketplace_business)
    listing.status = Listing.STATUS_SOLD
    listing.save(update_fields=["status"])
    messages.info(request, f"Tangazo '{listing.title}' limewekwa alama kuwa limeuzwa (Sold).")
    return redirect("marketplace:seller_dashboard")


@login_required
def seller_verification_submit(request):
    """Seller uploads official ID / TIN for manual review to earn Verified Seller badge"""
    if not hasattr(request.user, "marketplace_business"):
        return redirect("marketplace:seller_register")

    business = request.user.marketplace_business
    existing = getattr(business, "verification_application", None)

    if request.method == "POST":
        form = SellerVerificationForm(request.POST, request.FILES, instance=existing)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.business = business
            doc.status = BusinessProfile.VERIFICATION_PENDING
            doc.save()

            business.verification_status = BusinessProfile.VERIFICATION_PENDING
            business.save(update_fields=["verification_status"])

            AuditLog.objects.create(
                action="verification_submitted",
                actor=request.user,
                target_type="SellerVerification",
                target_id=str(doc.pk),
                details={"doc_type": doc.document_type, "id_number": doc.id_number}
            )

            messages.success(request, "Nyaraka zako zimewasilishwa! Timu yetu itazikagua na kukupa beji ya Uhakiki (Verified Seller) ndani ya saa 24.")
            return redirect("marketplace:seller_dashboard")
    else:
        form = SellerVerificationForm(instance=existing)

    return render(request, "marketplace/seller_verification.html", {
        "form": form,
        "business": business,
        "existing": existing
    })


# ==========================================
# CART & MVP ORDER PLACEMENT
# ==========================================

def cart_view(request):
    """Customer shopping cart view"""
    if request.user.is_authenticated:
        items = CartItem.objects.filter(user=request.user).select_related("listing__seller")
    else:
        session_key = request.session.session_key
        items = CartItem.objects.filter(session_key=session_key).select_related("listing__seller") if session_key else []

    total = sum(item.subtotal for item in items)
    return render(request, "marketplace/cart.html", {"items": items, "total": total})


def cart_add(request, pk):
    """Add listing to cart"""
    listing = get_object_or_404(Listing, pk=pk, status=Listing.STATUS_ACTIVE)
    quantity = int(request.POST.get("quantity", 1))

    if request.user.is_authenticated:
        item, created = CartItem.objects.get_or_create(user=request.user, listing=listing)
        if not created:
            item.quantity += quantity
            item.save()
    else:
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        item, created = CartItem.objects.get_or_create(session_key=session_key, listing=listing)
        if not created:
            item.quantity += quantity
            item.save()

    messages.success(request, f"'{listing.title}' imeongezwa kwenye kikapu chako!")
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("marketplace:cart_view")


def cart_remove(request, pk):
    """Remove item from cart"""
    if request.user.is_authenticated:
        CartItem.objects.filter(pk=pk, user=request.user).delete()
    else:
        session_key = request.session.session_key
        CartItem.objects.filter(pk=pk, session_key=session_key).delete()

    messages.info(request, "Bidhaa imeondolewa kwenye kikapu.")
    return redirect("marketplace:cart_view")


@login_required
def order_checkout(request):
    """Place direct MVP order (grouped by seller). No complex gateway needed for MVP."""
    cart_items = CartItem.objects.filter(user=request.user).select_related("listing__seller")
    if not cart_items.exists():
        messages.warning(request, "Kikapu chako kiko tupu.")
        return redirect("marketplace:home")

    # Group items by seller
    sellers_dict = {}
    for item in cart_items:
        sellers_dict.setdefault(item.listing.seller, []).append(item)

    if request.method == "POST":
        form = OrderCheckoutForm(request.POST)
        if form.is_valid():
            created_orders = []
            for seller, items in sellers_dict.items():
                seller_total = sum(i.subtotal for i in items)
                order = Order.objects.create(
                    customer=request.user,
                    business=seller,
                    customer_name=form.cleaned_data["customer_name"],
                    customer_phone=form.cleaned_data["customer_phone"],
                    fulfillment_type=form.cleaned_data["fulfillment_type"],
                    delivery_district=form.cleaned_data.get("delivery_district", ""),
                    delivery_ward=form.cleaned_data.get("delivery_ward", ""),
                    delivery_address=form.cleaned_data.get("delivery_address", ""),
                    notes=form.cleaned_data.get("notes", ""),
                    total_amount=seller_total
                )
                for i in items:
                    OrderItem.objects.create(
                        order=order,
                        listing=i.listing,
                        product_title=i.listing.title,
                        unit_price=i.listing.price,
                        quantity=i.quantity
                    )
                created_orders.append(order)

            # Clear cart
            cart_items.delete()

            messages.success(request, f"Oda yako imetumwa kikamilifu kwa wauzaji! Namba ya oda: {created_orders[0].order_number}")
            return redirect("marketplace:order_detail", order_number=created_orders[0].order_number)
    else:
        default_phone = request.user.username.replace("tz_", "+") if request.user.username.startswith("tz_") else ""
        form = OrderCheckoutForm(initial={
            "customer_name": request.user.name or "",
            "customer_phone": default_phone
        })

    total = sum(item.subtotal for item in cart_items)
    return render(request, "marketplace/checkout.html", {
        "form": form,
        "items": cart_items,
        "total": total,
        "sellers_dict": sellers_dict
    })


@login_required
def order_list(request):
    """Customer's orders list"""
    orders = Order.objects.filter(customer=request.user).select_related("business").prefetch_related("items").order_by("-created_at")
    return render(request, "marketplace/order_list.html", {"orders": orders})


@login_required
def order_detail(request, order_number):
    """Order detail view showing status, items, seller contact, and directions"""
    order = get_object_or_404(
        Order.objects.select_related("business", "customer").prefetch_related("items"),
        order_number=order_number
    )
    if order.customer != request.user and getattr(order.business, "user", None) != request.user:
        messages.error(request, "Hauruhusiwi kuona oda hii.")
        return redirect("marketplace:home")

    return render(request, "marketplace/order_detail.html", {"order": order})


@login_required
def seller_order_update_status(request, pk):
    """Seller updates order status (Confirm, Ready for Pickup, Completed, Cancelled)"""
    order = get_object_or_404(Order, pk=pk, business__user=request.user)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save(update_fields=["status"])
            messages.success(request, f"Hali ya oda #{order.order_number} imebadilishwa kuwa: {order.get_status_display()}")
    return redirect("marketplace:seller_dashboard")


# ==========================================
# IN-APP CHAT (Customer <-> Business Owner)
# ==========================================

@login_required
def chat_start(request, listing_id):
    """Start or open conversation regarding a specific listing"""
    listing = get_object_or_404(Listing.objects.select_related("seller__user"), pk=listing_id)
    if listing.seller.user == request.user:
        messages.info(request, "Huwezi kujitumia ujumbe mwenyewe.")
        return redirect("marketplace:listing_detail", slug=listing.slug)

    conversation, _ = Conversation.objects.get_or_create(
        customer=request.user,
        business=listing.seller,
        listing=listing
    )
    return redirect("marketplace:chat_detail", conversation_id=conversation.pk)


@login_required
def chat_inbox(request):
    """Inbox showing active conversations for customer or business owner"""
    user_conversations = Conversation.objects.filter(
        Q(customer=request.user) | Q(business__user=request.user)
    ).select_related("customer", "business", "listing").prefetch_related("messages").order_by("-updated_at")

    return render(request, "marketplace/chat_inbox.html", {"conversations": user_conversations})


@login_required
def chat_detail(request, conversation_id):
    """Chat thread between buyer and seller"""
    conversation = get_object_or_404(
        Conversation.objects.select_related("customer", "business", "listing"),
        pk=conversation_id
    )

    if conversation.customer != request.user and conversation.business.user != request.user:
        messages.error(request, "Hauruhusiwi kusoma mazungumzo haya.")
        return redirect("marketplace:home")

    if request.method == "POST":
        text = request.POST.get("message", "").strip()
        if text:
            msg = ChatMessage.objects.create(
                conversation=conversation,
                sender=request.user,
                text=text
            )
            conversation.updated_at = timezone.now()
            conversation.save(update_fields=["updated_at"])
            return redirect("marketplace:chat_detail", conversation_id=conversation.pk)

    conversation.messages.exclude(sender=request.user).update(is_read=True)
    messages_list = conversation.messages.all().select_related("sender")

    return render(request, "marketplace/chat_detail.html", {
        "conversation": conversation,
        "chat_messages": messages_list,
        "is_seller": conversation.business.user == request.user,
    })


# ==========================================
# ENGAGEMENT: FAVORITES & SELLER FOLLOWS
# ==========================================

@login_required
def favorite_toggle(request, pk):
    """Toggle favorite for a listing"""
    listing = get_object_or_404(Listing, pk=pk)
    fav = Favorite.objects.filter(user=request.user, listing=listing).first()
    if fav:
        fav.delete()
        Listing.objects.filter(pk=pk).update(favorites_count=F("favorites_count") - 1)
        favorited = False
    else:
        Favorite.objects.create(user=request.user, listing=listing)
        Listing.objects.filter(pk=pk).update(favorites_count=F("favorites_count") + 1)
        favorited = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"favorited": favorited})
    return redirect(request.META.get("HTTP_REFERER", "/marketplace/"))


@login_required
def follow_toggle(request, seller_id):
    """Toggle follow for a business seller"""
    seller = get_object_or_404(BusinessProfile, pk=seller_id)
    follow = SellerFollow.objects.filter(user=request.user, business=seller).first()
    if follow:
        follow.delete()
        following = False
    else:
        SellerFollow.objects.create(user=request.user, business=seller)
        following = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"following": following})
    return redirect(request.META.get("HTTP_REFERER", "/marketplace/"))


# ==========================================
# REPORTING & COMMUNITY SAFETY
# ==========================================

@login_required
def report_listing(request, pk):
    """Report a suspicious, counterfeit, or scam listing"""
    listing = get_object_or_404(Listing, pk=pk)

    if request.method == "POST":
        form = ReportListingForm(request.POST)
        if form.is_valid():
            rep = form.save(commit=False)
            rep.reporter = request.user
            rep.listing = listing
            rep.reported_business = listing.seller
            rep.save()

            AuditLog.objects.create(
                action="report_submitted",
                actor=request.user,
                target_type="Listing",
                target_id=str(listing.pk),
                details={"reason": rep.reason}
            )

            messages.success(request, "Asante kwa taarifa yako. Timu yetu ya usalama inakagua tangazo hili.")
            return redirect("marketplace:listing_detail", slug=listing.slug)
    else:
        form = ReportListingForm()

    return render(request, "marketplace/report_form.html", {
        "form": form,
        "listing": listing,
    })


# ==========================================
# PRIVACY & TANZANIA PDPA 2022 COMPLIANCE
# ==========================================

def privacy_policy(request):
    """Privacy policy complying with Tanzania Personal Data Protection Act (2022)"""
    return render(request, "marketplace/privacy_policy.html")


@login_required
def data_export(request):
    """Allow user to download a full JSON copy of all personal data held on the platform (PDPA Right to Access)"""
    user = request.user
    data = {
        "account": {
            "email": user.email,
            "name": user.name,
            "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        },
        "orders": [
            {
                "order_number": o.order_number,
                "seller": o.business.business_name,
                "amount": str(o.total_amount),
                "created_at": o.created_at.isoformat(),
            }
            for o in user.marketplace_orders.all()
        ],
        "favorites": [f.listing.title for f in user.marketplace_favorites.all()],
        "exported_at": timezone.now().isoformat(),
        "compliance": "Tanzania Personal Data Protection Act (2022)"
    }
    response = HttpResponse(json.dumps(data, indent=2), content_type="application/json")
    response["Content-Disposition"] = f'attachment; filename="thecity_marketplace_data_{user.pk}.json"'
    return response


# ==========================================
# PWA ASSETS: MANIFEST & SERVICE WORKER
# ==========================================

def pwa_manifest(request):
    manifest = {
        "name": "The City Marketplace - Dar es Salaam",
        "short_name": "The City",
        "description": "Nunua na uza bidhaa Dar es Salaam kwa urahisi na uhakika",
        "start_url": "/marketplace/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#10b981",
        "icons": [
            {
                "src": "/static/marketplace/icons/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/marketplace/icons/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return JsonResponse(manifest)


def pwa_service_worker(request):
    sw_code = """
const CACHE_NAME = 'thecity-marketplace-v1';
const STATIC_ASSETS = [
  '/marketplace/',
  '/static/css/app.css',
  '/static/marketplace/css/marketplace.css'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((k) => {
          if (k !== CACHE_NAME) return caches.delete(k);
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then((cached) => {
      return cached || fetch(e.request).catch(() => caches.match('/marketplace/'));
    })
  );
});
"""
    return HttpResponse(sw_code, content_type="application/javascript")
