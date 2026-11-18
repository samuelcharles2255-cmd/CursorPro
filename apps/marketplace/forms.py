from django import forms
from .models import (
    BusinessProfile, Listing, ListingImage, SellerVerification,
    Order, Report, DAR_DISTRICT_CHOICES, DAR_WARDS_BY_DISTRICT, Category
)


class PhoneRequestOTPForm(forms.Form):
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            "placeholder": "Mfano: 0712 345 678 au +255 7...",
            "class": "form-control",
            "type": "tel",
            "autocomplete": "tel"
        }),
        label="Namba ya Simu (Phone Number)"
    )
    user_type = forms.ChoiceField(
        choices=[("buyer", "Mteja / Buyer"), ("seller", "Muuzaji / Business Owner")],
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        initial="buyer",
        label="Aina ya Akaunti (Account Type)"
    )


class PhoneVerifyOTPForm(forms.Form):
    phone_number = forms.CharField(widget=forms.HiddenInput())
    user_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Jina lako kamili (Full Name)",
            "class": "form-control"
        }),
        label="Jina Lako (Your Name)"
    )
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            "placeholder": "123456",
            "class": "form-control text-center font-bold tracking-widest text-2xl",
            "autocomplete": "one-time-code",
            "pattern": "[0-9]*",
            "inputmode": "numeric"
        }),
        label="Ingiza Msimbo wa OTP (Enter 6-digit OTP)"
    )


class BusinessRegistrationForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = [
            "business_name", "tagline", "description", "phone_number",
            "whatsapp_number", "district", "ward", "street_address",
            "landmark_directions", "google_maps_url", "logo", "banner"
        ]
        widgets = {
            "business_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Mfano: Apex Electronics Ltd"}),
            "tagline": forms.TextInput(attrs={"class": "form-control", "placeholder": "Mfano: Vifaa Halisi vya Teknolojia na Elektroniki Dar es Salaam"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Eleza kuhusu biashara yako, bidhaa unazouza, na dhamana..."}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "07XXXXXXXX"}),
            "whatsapp_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "07XXXXXXXX (Kwa ajili ya WhatsApp)"}),
            "district": forms.Select(attrs={"class": "form-select", "id": "id_district"}),
            "ward": forms.TextInput(attrs={"class": "form-control", "placeholder": "Mfano: Kariakoo, Sinza, Masaki..."}),
            "street_address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Mtaa / Barabara (Mfano: Mtaa wa Kongo & Aggrey)"}),
            "landmark_directions": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Maelekezo wazi ya kufika dukani (Mfano: Mkabala na Benki ya CRDB, ghorofa ya 1)"}),
            "google_maps_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://maps.app.goo.gl/..."}),
            "logo": forms.FileInput(attrs={"class": "form-control"}),
            "banner": forms.FileInput(attrs={"class": "form-control"}),
        }


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            "title", "category", "price", "is_negotiable", "condition",
            "district", "ward", "pickup_available", "delivery_available",
            "description"
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Mfano: Apple MacBook Pro 14 M3 - 512GB SSD"}),
            "category": forms.Select(attrs={"class": "form-select", "id": "id_category"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Bei kwa TSh (Mfano: 1850000)"}),
            "is_negotiable": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "condition": forms.Select(attrs={"class": "form-select"}),
            "district": forms.Select(attrs={"class": "form-select", "id": "id_listing_district"}),
            "ward": forms.TextInput(attrs={"class": "form-control", "placeholder": "Wodi (Mfano: Kariakoo)"}),
            "pickup_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "delivery_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Eleza hali ya bidhaa, sifa zake kuu, rangi, kama ina warranty au risiti..."
            }),
        }


class SellerVerificationForm(forms.ModelForm):
    class Meta:
        model = SellerVerification
        fields = ["document_type", "id_number", "document_front", "document_back"]
        widgets = {
            "document_type": forms.Select(attrs={"class": "form-select"}),
            "id_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Namba ya kitambulisho (Mfano NIDA: 1990...)"}),
            "document_front": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "document_back": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }


class OrderCheckoutForm(forms.Form):
    customer_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Jina lako kamili"})
    )
    customer_phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Namba ya simu ya kupokea oda"})
    )
    fulfillment_type = forms.ChoiceField(
        choices=Order.FULFILLMENT_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        initial=Order.FULFILLMENT_PICKUP
    )
    delivery_district = forms.ChoiceField(
        choices=[("", "-- Chagua Wilaya / District --")] + DAR_DISTRICT_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    delivery_ward = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Wodi unayotaka kuletewa (Mfano: Sinza)"})
    )
    delivery_address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Mtaa / Jengo / Njia panda ya kufika"})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Ujumbe au maagizo ya ziada kwa muuzaji..."})
    )


class ReportListingForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason", "explanation"]
        widgets = {
            "reason": forms.Select(attrs={"class": "form-select"}),
            "explanation": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Tafadhali toa maelezo zaidi kuhusu tatizo uliloliona kwenye tangazo hili..."
            }),
        }
