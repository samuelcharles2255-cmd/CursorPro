import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Valid mobile network prefixes in Tanzania (MNOs: Vodacom, Airtel, Tigo, Halotel, TTCL, Smile)
# 74, 75, 76 (Vodacom)
# 68, 69, 78 (Airtel)
# 65, 67, 71 (Tigo)
# 61, 62     (Halotel)
# 73         (TTCL)
# 66         (Smile)
TZ_VALID_PREFIXES = (
    "74", "75", "76",
    "68", "69", "78",
    "65", "67", "71",
    "61", "62",
    "73",
    "66",
)

# Regex pattern matching valid raw Tanzanian mobile numbers in standard formats
TZ_PHONE_PATTERN = re.compile(
    r'^(?:\+?255|0)?([67]\d{8})$'
)


def normalize_tz_phone(phone_number: str | None) -> str | None:
    """
    Normalizes a Tanzanian phone number into standard E.164 format: +255XXXXXXXXX.
    Strips whitespace, hyphens, and brackets.
    Returns None if empty.
    """
    if not phone_number:
        return None

    cleaned = re.sub(r'[\s\-\(\)\.]', '', str(phone_number).strip())
    match = TZ_PHONE_PATTERN.match(cleaned)
    if not match:
        return cleaned

    national_number = match.group(1)
    return f"+255{national_number}"


def validate_tz_phone(value: str) -> None:
    """
    Validates that a string is a valid Tanzanian mobile phone number.
    Ensures correct length and authentic Tanzanian mobile network prefixes.
    """
    if not value:
        return

    cleaned = re.sub(r'[\s\-\(\)\.]', '', str(value).strip())
    match = TZ_PHONE_PATTERN.match(cleaned)
    if not match:
        raise ValidationError(
            _("Invalid Tanzania phone number format. Must start with +255, 255, 06, or 07 (e.g. +255712345678 or 0712345678)."),
            code="invalid_tz_phone"
        )

    national_number = match.group(1)
    prefix = national_number[:2]
    if prefix not in TZ_VALID_PREFIXES:
        raise ValidationError(
            _(f"Invalid mobile operator code '0{prefix}'. Valid prefixes include Vodacom (074/075/076), Airtel (068/069/078), Tigo (065/067/071), Halotel (061/062), and TTCL (073)."),
            code="invalid_tz_prefix"
        )
