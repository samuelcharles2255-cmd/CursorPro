from django import template
from decimal import Decimal

register = template.Library()


@register.simple_tag(takes_context=True)
def t(context, sw_text, en_text=""):
    """Bilingual translator helper for Swahili and English UI. Defaults to Swahili first-class."""
    request = context.get("request")
    lang = "sw"
    if request and hasattr(request, "session"):
        lang = request.session.get("lang", "sw")
    elif request and hasattr(request, "COOKIES"):
        lang = request.COOKIES.get("lang", "sw")

    if lang == "en" and en_text:
        return en_text
    return sw_text


@register.filter
def tzs(value):
    """Formats numeric price into Tanzanian Shillings format: TSh 1,250,000"""
    if value is None or value == "":
        return "TSh 0"
    try:
        dec = Decimal(str(value))
        return f"TSh {dec:,.0f}"
    except Exception:
        return f"TSh {value}"


@register.filter
def wa_number(value):
    """Clean phone number for wa.me links"""
    raw = "".join(filter(str.isdigit, str(value or "")))
    if raw.startswith("0") and len(raw) == 10:
        return "255" + raw[1:]
    return raw
