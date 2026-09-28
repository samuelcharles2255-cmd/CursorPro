"""
Pulls job listings from Jooble's REST API and upserts them into Job/Company.

Jooble API docs: https://help.jooble.org/en/support/solutions/articles/60001448238

Known limits of this source (read before you rely on it):
  - `link` usually routes through Jooble, not straight to the employer's
    page — check real responses before assuming it matches your "tap job
    -> land on company page" flow.
  - Jooble returns a `snippet`, not a full job description.
  - `salary` is free text ("$80,000 - $100,000") — parsing it is best
    effort and WILL fail on some formats. salary_min/max just stay null
    when it does; nothing crashes.
  - Jooble gives no `country` and no `expires_at` — country comes from
    whatever you pass into the search, and stale-job expiry isn't
    handled here at all.
"""
import logging
import re
from datetime import datetime

import requests
from django.conf import settings
from django.utils import timezone

from apps.jobs.cleaning import clean_job_description
from apps.jobs.models import Company, Job

logger = logging.getLogger(__name__)

JOOBLE_API_URL = "https://jooble.org/api/{api_key}"

# Jooble's `type` is free text ("Full-time", "Part time", "Temporary"...).
# Only map what we recognize onto our fixed choices — anything unrecognized
# is left blank rather than guessed.
EMPLOYMENT_TYPE_MAP = {
    "full-time": "full_time",
    "full time": "full_time",
    "part-time": "part_time",
    "part time": "part_time",
    "contract": "contract",
    "temporary": "contract",
    "internship": "internship",
    "freelance": "freelance",
}

SALARY_NUMBERS = re.compile(r"[\d,]+(?:\.\d+)?")
CURRENCY_SYMBOLS = {"$": "USD", "£": "GBP", "€": "EUR", "₦": "NGN"}


class JoobleAPIError(Exception):
    pass


def _normalize_employment_type(raw_type):
    if not raw_type:
        return ""
    return EMPLOYMENT_TYPE_MAP.get(raw_type.strip().lower(), "")


def _parse_salary(raw_salary):
    """Best-effort only. Returns (min, max, currency) — any of which can be None/''."""
    if not raw_salary:
        return None, None, ""

    numbers = SALARY_NUMBERS.findall(raw_salary)
    if not numbers:
        return None, None, ""

    try:
        values = [float(n.replace(",", "")) for n in numbers[:2]]
    except ValueError:
        return None, None, ""

    salary_min = values[0]
    salary_max = values[1] if len(values) > 1 else values[0]

    currency = ""
    for symbol, code in CURRENCY_SYMBOLS.items():
        if symbol in raw_salary:
            currency = code
            break
    else:
        code_match = re.search(r"\b[A-Z]{3}\b", raw_salary)
        if code_match:
            currency = code_match.group(0)

    return salary_min, salary_max, currency


def _parse_datetime(raw):
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(raw)
    except (ValueError, TypeError):
        logger.warning("Could not parse Jooble date: %r", raw)
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    return dt


def fetch_jooble_jobs(keywords, location="", radius=None, salary=None, page=1, results_per_page=20):
    """Calls the Jooble API directly and returns the raw list of job dicts (no DB writes)."""
    api_key = getattr(settings, "JOOBLE_API_KEY", None)
    if not api_key:
        raise JoobleAPIError("JOOBLE_API_KEY is not set in settings.py")

    payload = {"keywords": keywords, "location": location, "page": str(page)}
    if radius is not None:
        payload["radius"] = str(radius)
    if salary is not None:
        payload["salary"] = salary
    if results_per_page:
        payload["ResultOnPage"] = results_per_page

    try:
        response = requests.post(JOOBLE_API_URL.format(api_key=api_key), json=payload, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise JoobleAPIError(f"Jooble request failed: {exc}") from exc

    return response.json().get("jobs", [])


def sync_jooble_jobs(keywords, location="", country="", **kwargs):
    """
    Fetches from Jooble and upserts into Job. Safe to re-run — relies on
    the (source, source_job_id) unique constraint on Job to update
    existing rows instead of duplicating them on every sync.

    Returns (created_count, updated_count, skipped_count).
    """
    raw_jobs = fetch_jooble_jobs(keywords, location=location, **kwargs)

    created = updated = skipped = 0

    for raw in raw_jobs:
        job_id = raw.get("id")
        title = (raw.get("title") or "").strip()
        application_url = (raw.get("link") or "").strip()

        # a job with no id, title or apply link isn't usable — don't store junk
        if not job_id or not title or not application_url:
            skipped += 1
            continue

        company_name = (raw.get("company") or "Unknown").strip()
        company, _ = Company.objects.get_or_create(name=company_name)

        salary_min, salary_max, currency = _parse_salary(raw.get("salary"))

        defaults = {
            "title": title,
            "company": company,
            "location": (raw.get("location") or "").strip(),
            "country": country,  # Jooble doesn't return this — it comes from your search call
            "description": clean_job_description(raw.get("snippet", ""), source=Job.SOURCE_API),
            "employment_type": _normalize_employment_type(raw.get("type")),
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_currency": currency,
            "application_url": application_url,
            "source": Job.SOURCE_API,
            "posted_at": _parse_datetime(raw.get("updated")),
        }

        _, was_created = Job.objects.update_or_create(
            source=Job.SOURCE_API,
            source_job_id=str(job_id),
            defaults=defaults,
        )
        created += int(was_created)
        updated += int(not was_created)

    logger.info("Jooble sync '%s': %s created, %s updated, %s skipped", keywords, created, updated, skipped)
    return created, updated, skipped