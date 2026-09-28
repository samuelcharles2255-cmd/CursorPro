import logging
import re
from datetime import datetime, timedelta, timezone as py_timezone
from urllib.parse import urljoin, urlparse

import requests
from django.utils import timezone

from apps.jobs.cleaning import clean_job_description

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
}

WORKDAY_TIME_TYPE_MAP = {
    "full time": "full_time",
    "full_time": "full_time",
    "part time": "part_time",
    "part_time": "part_time",
    "contract": "contract",
    "temporary": "contract",
    "intern": "internship",
    "internship": "internship",
}


def to_workday_cxs_url(url):
    """
    Given a Workday career site URL or CXS endpoint, ensure it points to the
    Candidate Experience Service (CXS) search endpoint.

    Examples:
        Input:  https://salesforce.wd12.myworkdayjobs.com/en-US/External_Career_Site
        Output: https://salesforce.wd12.myworkdayjobs.com/wday/cxs/salesforce/External_Career_Site/jobs

        Input:  https://salesforce.wd12.myworkdayjobs.com/wday/cxs/salesforce/External_Career_Site/jobs
        Output: https://salesforce.wd12.myworkdayjobs.com/wday/cxs/salesforce/External_Career_Site/jobs
    """
    if not url:
        return ""

    url = url.strip()
    if "/wday/cxs/" in url and url.endswith("/jobs"):
        return url

    parsed = urlparse(url)
    host = parsed.netloc
    if not host:
        return url

    # Extract tenant from hostname (e.g. 'salesforce' from 'salesforce.wd12.myworkdayjobs.com')
    tenant = host.split(".")[0]

    # Filter out language segments like 'en-US', 'fr-FR'
    path_parts = [
        p for p in parsed.path.strip("/").split("/")
        if p and not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", p, re.I)
    ]
    site = path_parts[0] if path_parts else "External"

    return f"{parsed.scheme or 'https'}://{host}/wday/cxs/{tenant}/{site}/jobs"


def _extract_base_career_url(api_url):
    """
    Extracts the root career site URL from a CXS endpoint to construct full job detail URLs.
    Example:
        From: https://salesforce.wd12.myworkdayjobs.com/wday/cxs/salesforce/External_Career_Site/jobs
        To:   https://salesforce.wd12.myworkdayjobs.com/en-US/External_Career_Site
    """
    parsed = urlparse(api_url)
    cxs_match = re.search(r"/wday/cxs/([^/]+)/([^/]+)", parsed.path)
    if cxs_match:
        site = cxs_match.group(2)
        return f"{parsed.scheme}://{parsed.netloc}/en-US/{site}"
    return f"{parsed.scheme}://{parsed.netloc}"


def fetch_workday_jobs(
    api_url,
    method=None,
    headers=None,
    params=None,
    payload=None,
    limit=50,
):
    """
    Fetch jobs from a Workday endpoint.
    Automatically handles CXS POST JSON endpoints as well as classic GET endpoints.
    """
    req_headers = {**DEFAULT_HEADERS, **(headers or {})}
    endpoint = to_workday_cxs_url(api_url)

    # Determine whether to use POST or GET
    use_post = method.upper() == "POST" if method else ("/wday/cxs/" in endpoint)

    if use_post:
        json_payload = payload or {
            "appliedFacets": {},
            "limit": limit,
            "offset": 0,
            "searchText": "",
        }
        try:
            response = requests.post(
                endpoint,
                headers=req_headers,
                params=params,
                json=json_payload,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 405:
                # Fallback to GET
                logger.info("Workday POST returned 405 on %s, trying GET", endpoint)
            else:
                logger.error("Failed to fetch Workday jobs via POST from %s: %s", endpoint, exc)
                raise
        except requests.RequestException as exc:
            logger.error("Failed to fetch Workday jobs from %s: %s", endpoint, exc)
            raise

    # GET fallback / standard request
    try:
        response = requests.get(
            endpoint,
            headers=req_headers,
            params=params or {"limit": limit},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.error("Failed to fetch Workday jobs via GET from %s: %s", endpoint, exc)
        raise


def _parse_workday_date(raw_date):
    """Parses Workday date strings or relative strings like 'Posted Today', 'Posted 3 Days Ago'."""
    if not raw_date:
        return None

    text = str(raw_date).strip()

    # Relative dates
    now = timezone.now()
    lower = text.lower()
    if "today" in lower:
        return now
    if "yesterday" in lower:
        return now - timedelta(days=1)

    days_match = re.search(r"(\d+)\s+days?\s+ago", lower)
    if days_match:
        days = int(days_match.group(1))
        return now - timedelta(days=days)

    if "30+" in lower:
        return now - timedelta(days=30)

    # ISO or formatted date string
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
        return dt
    except (ValueError, TypeError):
        pass

    return None


def normalize_workday_job(job, base_site_url=None):
    """
    Normalize a Workday job into the format expected by import_jobs.
    Returns only fields that map directly to Job model fields
    (company FK is resolved by the command, not here).
    """
    # Extract source job id
    bullets = job.get("bulletFields")
    first_bullet = bullets[0] if isinstance(bullets, list) and bullets else ""
    source_job_id = str(job.get("id") or job.get("jobId") or first_bullet or "").strip()

    # Extract application URL
    raw_path = (
        job.get("externalPath")
        or job.get("jobUrl")
        or job.get("externalUrl")
        or job.get("url")
        or ""
    ).strip()

    if raw_path.startswith("http://") or raw_path.startswith("https://"):
        application_url = raw_path
    elif base_site_url and raw_path:
        application_url = urljoin(base_site_url + "/", raw_path.lstrip("/"))
    else:
        application_url = raw_path

    # Extract location
    loc = (
        job.get("locationsText")
        or job.get("location")
        or job.get("locations")
        or ""
    )
    if isinstance(loc, list):
        loc = ", ".join(str(item) for item in loc if item)
    elif not isinstance(loc, str):
        loc = str(loc)

    # Extract employment type
    raw_type = (
        job.get("timeType")
        or job.get("employmentType")
        or job.get("workerType")
        or ""
    ).strip().lower()
    employment_type = WORKDAY_TIME_TYPE_MAP.get(raw_type, "")

    # Posted date
    posted_at = _parse_workday_date(job.get("postedOn") or job.get("postedDate") or job.get("startDate"))

    title = (job.get("title") or job.get("jobTitle") or "").strip()
    raw_desc = job.get("description") or job.get("jobDescription") or ""
    desc = clean_job_description(raw_desc, source="career_page") if raw_desc else ""

    return {
        "title": title,
        "description": desc,
        "location": loc.strip(),
        "country": "",
        "application_url": application_url,
        "source": "career_page",
        "source_job_id": source_job_id,
        "employment_type": employment_type,
        "salary_min": None,
        "salary_max": None,
        "salary_currency": "",
        "posted_at": posted_at,
    }


def get_workday_jobs(
    api_url,
    method=None,
    headers=None,
    params=None,
    payload=None,
    limit=50,
):
    """
    Fetch and normalize Workday jobs.
    Returns a list of dicts ready for import_jobs to save.
    """
    data = fetch_workday_jobs(
        api_url=api_url,
        method=method,
        headers=headers,
        params=params,
        payload=payload,
        limit=limit,
    )

    if isinstance(data, list):
        raw_jobs = data
    else:
        raw_jobs = data.get("jobPostings") or data.get("jobs") or []

    base_site_url = _extract_base_career_url(api_url)

    normalized = []
    for item in raw_jobs[:limit]:
        norm = normalize_workday_job(item, base_site_url=base_site_url)
        normalized.append(norm)

    return normalized
