import os
import random
import logging
import re
import urllib.request
import urllib.parse
import json
import base64
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from apps.marketplace.models import PhoneOTP

logger = logging.getLogger(__name__)


def normalize_tz_phone(phone_number: str) -> str:
    """Normalize a Tanzanian phone number into canonical +255XXXXXXXXX format"""
    raw = re.sub(r"[^\d+]", "", str(phone_number or "").strip())
    if raw.startswith("+255"):
        digits = raw[4:]
    elif raw.startswith("255"):
        digits = raw[3:]
    elif raw.startswith("0"):
        digits = raw[1:]
    else:
        digits = raw

    return f"+255{digits}"


class OTPService:
    EXPIRY_MINUTES = 10
    MAX_ATTEMPTS = 5
    RATE_LIMIT_MINUTES = 10
    RATE_LIMIT_MAX_COUNT = 5

    @classmethod
    def _dispatch_live_sms(cls, recipient: str, text: str) -> bool:
        """Attempt sending via real SMS gateways (Beem Africa, Twilio, Africa's Talking) if configured in .env"""
        # 1. Beem Africa (Tanzania native: Vodacom, Tigo, Airtel, Halotel)
        beem_key = os.getenv("BEEM_API_KEY")
        beem_secret = os.getenv("BEEM_SECRET_KEY")
        beem_sender = os.getenv("BEEM_SENDER_ID", "INFO")
        if beem_key and beem_secret:
            try:
                dest = recipient.replace("+", "")
                payload = {
                    "source_addr": beem_sender,
                    "schedule_time": "",
                    "encoding": 0,
                    "message": text,
                    "recipients": [{"recipient_id": 1, "dest_addr": dest}]
                }
                creds = f"{beem_key}:{beem_secret}".encode("utf-8")
                auth_header = "Basic " + base64.b64encode(creds).decode("utf-8")
                req = urllib.request.Request(
                    "https://api.beem.africa/v1/send-sms",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": auth_header,
                        "User-Agent": "AtriumMarketplace/1.0"
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status in (200, 201):
                        logger.info(f"[SMS DISPATCH SUCCESS - BEEM AFRICA] Sent to {recipient}")
                        return True
            except Exception as e:
                logger.error(f"[SMS DISPATCH ERROR - BEEM AFRICA] {e}")

        # 2. Twilio
        twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_from = os.getenv("TWILIO_PHONE_NUMBER")
        if twilio_sid and twilio_token and twilio_from:
            try:
                url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
                data = urllib.parse.urlencode({
                    "To": recipient,
                    "From": twilio_from,
                    "Body": text
                }).encode("utf-8")
                creds = f"{twilio_sid}:{twilio_token}".encode("utf-8")
                auth_header = "Basic " + base64.b64encode(creds).decode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={
                        "Authorization": auth_header,
                        "User-Agent": "AtriumMarketplace/1.0"
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status in (200, 201):
                        logger.info(f"[SMS DISPATCH SUCCESS - TWILIO] Sent to {recipient}")
                        return True
            except Exception as e:
                logger.error(f"[SMS DISPATCH ERROR - TWILIO] {e}")

        # 3. Africa's Talking
        at_username = os.getenv("AFRICASTALKING_USERNAME")
        at_key = os.getenv("AFRICASTALKING_API_KEY")
        at_sender = os.getenv("AFRICASTALKING_SENDER_ID")
        if at_username and at_key:
            try:
                url = "https://api.africastalking.com/version1/messaging"
                post_fields = {
                    "username": at_username,
                    "to": recipient,
                    "message": text
                }
                if at_sender:
                    post_fields["from"] = at_sender
                data = urllib.parse.urlencode(post_fields).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={
                        "apiKey": at_key,
                        "Accept": "application/json",
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status in (200, 201):
                        logger.info(f"[SMS DISPATCH SUCCESS - AFRICASTALKING] Sent to {recipient}")
                        return True
            except Exception as e:
                logger.error(f"[SMS DISPATCH ERROR - AFRICASTALKING] {e}")

        return False

    @classmethod
    def send_otp(cls, phone_number: str, purpose: str = PhoneOTP.PURPOSE_LOGIN) -> dict:
        normalized = normalize_tz_phone(phone_number)
        now = timezone.now()

        # Check rate limit (relaxed in development/debug mode to prevent developer lockouts)
        max_recent = 50 if settings.DEBUG else cls.RATE_LIMIT_MAX_COUNT
        recent_count = PhoneOTP.objects.filter(
            phone_number=normalized,
            created_at__gte=now - timedelta(minutes=cls.RATE_LIMIT_MINUTES)
        ).count()

        if recent_count >= max_recent:
            return {
                "success": False,
                "error": "Tafadhali subiri dakika chache kabla ya kuomba msimbo mpya (Rate limit reached).",
                "rate_limited": True
            }

        # Invalidate old unused OTPs for this phone and purpose
        PhoneOTP.objects.filter(
            phone_number=normalized,
            purpose=purpose,
            is_used=False
        ).update(is_used=True)

        # Generate 6-digit code
        otp_code = f"{random.randint(100000, 999999)}"
        expires_at = now + timedelta(minutes=cls.EXPIRY_MINUTES)

        otp_record = PhoneOTP.objects.create(
            phone_number=normalized,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=expires_at
        )

        message_text = f"Msimbo wako wa uthibitisho wa Atrium Marketplace ni {otp_code}. Msimbo huu utaisha baada ya dakika 10."

        # Attempt live SMS dispatch
        live_sent = cls._dispatch_live_sms(normalized, message_text)

        logger.info(f"[SMS SERVICE] To: {normalized} | LiveSent: {live_sent} | Code: {otp_code}")
        print(f"\n==========================================")
        print(f"[ATRIUM SMS SERVICE] To: {normalized}")
        print(f"OTP Code: {otp_code}")
        print(f"Live SMS Gateway Dispatched: {live_sent}")
        print(f"==========================================\n")

        return {
            "success": True,
            "phone_number": normalized,
            "otp_code": otp_code,
            "live_sent": live_sent,
            "expires_in_minutes": cls.EXPIRY_MINUTES
        }

    @classmethod
    def verify_otp(cls, phone_number: str, code: str, purpose: str = PhoneOTP.PURPOSE_LOGIN) -> dict:
        normalized = normalize_tz_phone(phone_number)
        code = str(code).strip()

        otp_record = PhoneOTP.objects.filter(
            phone_number=normalized,
            purpose=purpose,
            is_used=False
        ).order_by("-created_at").first()

        if not otp_record:
            return {"success": False, "error": "Msimbo haupatikani au ulishatumika."}

        if timezone.now() > otp_record.expires_at:
            otp_record.is_used = True
            otp_record.save(update_fields=["is_used"])
            return {"success": False, "error": "Msimbo umepitwa na wakati (Expired). Omba msimbo mpya."}

        if otp_record.attempts >= cls.MAX_ATTEMPTS:
            otp_record.is_used = True
            otp_record.save(update_fields=["is_used"])
            return {"success": False, "error": "Umejaribu mara nyingi bila mafanikio. Omba msimbo mpya."}

        if otp_record.otp_code != code:
            otp_record.attempts += 1
            otp_record.save(update_fields=["attempts"])
            return {
                "success": False,
                "error": f"Msimbo si sahihi. Majaribio yaliyobaki: {cls.MAX_ATTEMPTS - otp_record.attempts}"
            }

        otp_record.is_used = True
        otp_record.save(update_fields=["is_used"])
        return {"success": True, "phone_number": normalized}
