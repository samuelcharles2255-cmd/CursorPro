import logging
from datetime import datetime, timezone as py_timezone

import requests

from apps.jobs.cleaning import clean_job_description

logger = logging.getLogger(__name__)

BASE_URL = "https://api.lever.co/v0/postings"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

COMMITMENT_MAP = {
    "full-time": "full_time",
    "full time": "full_time",
    "part-time": "part_time",
    "part time": "part_time",
    "contract": "contract",
    "temporary": "contract",
    "internship": "internship",
    "intern": "internship",
    "freelance": "freelance",
}


def fetch_lever_jobs(company_slug):
    """
    Fetch all published jobs from a Lever company job board.

    Example:
        company_slug = "netflix" or "leverdemo"

    Returns:
        A list of raw Lever job dictionaries.
    """
    url = f"{BASE_URL}/{company_slug.strip()}"

    try:
        response = requests.get(
            url,
            params={"mode": "json"},
            headers=DEFAULT_HEADERS,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.error("Failed to fetch Lever jobs for %s: %s", company_slug, exc)
        raise


def _normalize_commitment(commitment_str):
    if not commitment_str:
        return ""
    val = commitment_str.strip().lower()
    return COMMITMENT_MAP.get(val, "")


def normalize_lever_job(job):
    """
    Convert a Lever job into the format expected by import_jobs.
    Returns only fields that map directly to Job model fields
    (company FK is resolved by the command, not here).
    """
    categories = job.get("categories") or {}

    location = categories.get("location", "")
    if not location and "allLocations" in categories:
        locs = categories.get("allLocations") or []
        if locs:
            location = locs[0]

    country = job.get("country") or categories.get("country") or ""
    raw_commitment = categories.get("commitment", "")
    employment_type = _normalize_commitment(raw_commitment)

    posted_at = None
    created_at_ms = job.get("createdAt")
    if created_at_ms:
        try:
            posted_at = datetime.fromtimestamp(created_at_ms / 1000.0, tz=py_timezone.utc)
        except (ValueError, TypeError, OSError):
            posted_at = None

    raw_desc = job.get("description") or job.get("descriptionPlain") or ""
    desc = clean_job_description(raw_desc, source="career_page") if raw_desc else ""

    return {
        "title": job.get("text", "").strip(),
        "description": desc,
        "location": location.strip() if isinstance(location, str) else str(location),
        "country": country.strip() if isinstance(country, str) else str(country),
        "application_url": job.get("hostedUrl") or job.get("applyUrl") or "",
        "source": "career_page",
        "source_job_id": str(job.get("id", "")),
        "employment_type": employment_type,
        "salary_min": None,
        "salary_max": None,
        "salary_currency": "",
        "posted_at": posted_at,
    }


def get_lever_jobs(company_slug, limit=None):
    """
    Fetch and normalize Lever jobs in one call.
    Returns a list of dicts ready for import_jobs to save.
    """
    raw_jobs = fetch_lever_jobs(company_slug)
    if limit and limit > 0:
        raw_jobs = raw_jobs[:limit]

    return [normalize_lever_job(job) for job in raw_jobs]
