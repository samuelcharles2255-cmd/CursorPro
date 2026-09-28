import html
import logging
from datetime import datetime

import requests
from django.utils import timezone

from apps.jobs.cleaning import clean_job_description

logger = logging.getLogger(__name__)

BASE_URL = "https://boards-api.greenhouse.io/v1/boards"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def fetch_greenhouse_jobs(company_token):
    """
    Fetch all currently published jobs from a Greenhouse job board.

    Example:
        company_token = "stripe"

    Returns:
        A list of raw Greenhouse job dictionaries.
    """
    url = f"{BASE_URL}/{company_token.strip()}/jobs"

    try:
        response = requests.get(
            url,
            params={"content": "true"},
            headers=DEFAULT_HEADERS,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("jobs", [])
    except requests.RequestException as exc:
        logger.error("Failed to fetch Greenhouse jobs for %s: %s", company_token, exc)
        raise


def _parse_greenhouse_date(date_str):
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str)
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
        return dt
    except (ValueError, TypeError):
        return None


def normalize_greenhouse_job(job):
    """
    Convert a Greenhouse job into the format expected by import_jobs.
    Returns only fields that map directly to Job model fields
    (company FK is resolved by the command, not here).
    """
    location = job.get("location") or {}
    loc_name = ""
    if isinstance(location, dict):
        loc_name = location.get("name", "")
    elif isinstance(location, str):
        loc_name = location

    # Clean and sanitize HTML content if present
    content = job.get("content", "")
    if content:
        content = clean_job_description(content, source="career_page")

    posted_at = _parse_greenhouse_date(job.get("updated_at") or job.get("first_published"))

    return {
        "title": job.get("title", "").strip(),
        "description": content,
        "location": loc_name.strip(),
        "country": "",
        "application_url": job.get("absolute_url", ""),
        "source": "career_page",
        "source_job_id": str(job.get("id", "")),
        "employment_type": "",
        "salary_min": None,
        "salary_max": None,
        "salary_currency": "",
        "posted_at": posted_at,
    }


def get_greenhouse_jobs(company_token, limit=None):
    """
    Fetch and normalize Greenhouse jobs in one call.
    Returns a list of dicts ready for import_jobs to save.
    """
    raw_jobs = fetch_greenhouse_jobs(company_token)
    if limit and limit > 0:
        raw_jobs = raw_jobs[:limit]

    return [normalize_greenhouse_job(job) for job in raw_jobs]
