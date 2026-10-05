"""CRDB Bank Careers – https://careers.crdbbank.co.tz/jobs

Direct REST API scraper for CRDB Bank's recruitment portal:
- Listing: https://careers.crdbbank.co.tz/api/v1/requisitions/job-posts/open
- Detail:  https://careers.crdbbank.co.tz/api/v1/requisitions/job-posts/{id}

Plain HTTP (requests) fetches full structured vacancy data without needing
Playwright or a headless browser.
"""
from __future__ import annotations

import logging
from typing import Iterator

from .base import BaseScraper, NormalizedJob, clean_text, parse_date

log = logging.getLogger("jobs.scrapers")

BASE_URL = "https://careers.crdbbank.co.tz"
OPEN_JOBS_API = f"{BASE_URL}/api/v1/requisitions/job-posts/open"
JOB_DETAIL_API = f"{BASE_URL}/api/v1/requisitions/job-posts"
CAREERS_PAGE = f"{BASE_URL}/jobs"
COMPANY_NAME = "CRDB Bank Plc"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}


def _normalize_crdb_location(raw_loc: str) -> str:
    """Map CRDB branch / office strings to clean geographic locations."""
    s = (raw_loc or "").strip()
    if not s:
        return "Tanzania"
    s_lower = s.lower()
    if "head office" in s_lower or "tanzania" in s_lower:
        return "Dar es Salaam, Tanzania"
    if "drc" in s_lower or "congo" in s_lower:
        return "Democratic Republic of the Congo"
    if "burundi" in s_lower:
        return "Burundi"
    return s


def _map_employment_type(terms: str | None) -> str:
    if not terms:
        return ""
    terms_upper = str(terms).upper()
    if "PERMANENT" in terms_upper or "FULL" in terms_upper:
        return "full_time"
    if "CONTRACT" in terms_upper or "FIXED" in terms_upper:
        return "contract"
    if "INTERN" in terms_upper:
        return "internship"
    if "PART" in terms_upper:
        return "part_time"
    return ""


class CRDBBankScraper(BaseScraper):
    """Scrapes all open vacancies from CRDB Bank recruitment API."""

    key = "crdb_bank"
    source_name = "CRDB Bank Careers"
    company_name = COMPANY_NAME
    db_source = "career_page"
    respect_robots = False  # internal JSON REST API

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session.headers.update(DEFAULT_HEADERS)

    def fetch(self) -> Iterator[NormalizedJob]:
        page = 0
        seen_count = 0

        while True:
            params = {
                "pageNumber": page,
                "pageSize": 50,
                "status": "INTERVIEW",
            }
            try:
                resp = self.get(OPEN_JOBS_API, params=params)
                data = resp.json().get("data", {})
            except Exception as exc:
                log.warning("[%s] Failed fetching page %d: %s", self.key, page, exc)
                break

            items = data.get("content", [])
            if not items:
                break

            total_pages = data.get("totalPages", 1)

            for item in items:
                job_id = item.get("id")
                if not job_id:
                    continue

                raw_title = item.get("title") or ""
                title = clean_text(raw_title)
                raw_loc = item.get("location") or ""
                location = _normalize_crdb_location(raw_loc)
                deadline_str = item.get("deadline")
                deadline = parse_date(deadline_str)

                # Fetch full job detail (purpose, responsibilities, qualifications)
                description = self._fetch_description(job_id, item)

                apply_url = CAREERS_PAGE
                source_url = CAREERS_PAGE

                yield NormalizedJob(
                    source=self.key,
                    title=title,
                    organization=self.company_name,
                    location=location,
                    deadline=deadline,
                    description=description,
                    apply_url=apply_url,
                    source_url=source_url,
                    external_id=f"crdb:{job_id}",
                )

                seen_count += 1
                if self.limit and seen_count >= self.limit:
                    return

            page += 1
            if page >= total_pages:
                break

    def _fetch_description(self, job_id: int, summary_item: dict) -> str:
        """Fetch rich description from detail API endpoint."""
        detail_url = f"{JOB_DETAIL_API}/{job_id}"
        try:
            r = self.session.get(detail_url, timeout=self.timeout)
            if r.status_code == 200:
                det = r.json().get("data", {}).get("details", {})
                parts = []

                unit = det.get("costCenterName") or summary_item.get("businessUnit")
                if unit:
                    parts.append(f"<p><strong>Department:</strong> {clean_text(unit)}</p>")

                terms = det.get("employmentTerms")
                if terms:
                    parts.append(f"<p><strong>Employment Terms:</strong> {clean_text(terms)}</p>")

                if det.get("jobPurpose"):
                    parts.append(f"<h3>Job Purpose</h3>{det['jobPurpose']}")

                if det.get("principalResponsibilities"):
                    parts.append(f"<h3>Key Responsibilities</h3>{det['principalResponsibilities']}")

                if det.get("qualificationRequired"):
                    parts.append(f"<h3>Qualifications &amp; Requirements</h3>{det['qualificationRequired']}")

                if det.get("footer"):
                    parts.append(det["footer"])

                if parts:
                    return "\n".join(parts)
        except Exception as exc:
            log.debug("[%s] Detail fetch failed for %d: %s", self.key, job_id, exc)

        # Fallback to summary info if detail fails
        unit = summary_item.get("businessUnit")
        unit_str = f" in {unit}" if unit else ""
        return f"<p>Open vacancy for {summary_item.get('title', '')}{unit_str} at CRDB Bank Plc.</p>"
