"""Ekazi.co.tz scraper – https://ekazi.co.tz

Ekazi is a Vite/React SPA, so the HTML shell is empty. However, it uses a
backend REST API at https://api.ekazi.co.tz/api/jobs which returns full
structured JSON without any auth requirement.

Response schema:
  {
    "data": [...],        # array of job objects
    "current_page": 1,
    "per_page": 10,
    "total_pages": 2,
    "total": 15
  }

Job object key fields:
  - id
  - title (often null; fall back to job_position.position_name)
  - dead_line
  - published / status
  - client.client_name  (company; show_client_name=0 means confidential)
  - job_position.position_name
  - job_duties.main_duties  (HTML)
  - job_addresses[].sub_location
  - job_external_url (if set, apply there)
  - job_email (if set, apply by email)
"""
from __future__ import annotations

import logging
from typing import Iterator

from .base import BaseScraper, NormalizedJob, clean_text, parse_date

log = logging.getLogger("jobs.scrapers")

API_BASE = "https://api.ekazi.co.tz/api/jobs"
PORTAL_URL = "https://ekazi.co.tz"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


class EkaziScraper(BaseScraper):
    """Scrapes job listings from Ekazi Tanzania (REST API)."""

    key = "ekazi"
    source_name = "Ekazi Tanzania"
    db_source = "api"
    respect_robots = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session.headers.update(HEADERS)

    def fetch(self) -> Iterator[NormalizedJob]:
        page = 1
        count = 0

        while True:
            try:
                resp = self.get(API_BASE, params={"page": page, "per_page": 20})
                payload = resp.json()
            except Exception as exc:
                log.warning("[ekazi] fetch failed page %d: %s", page, exc)
                break

            jobs = payload.get("data", [])
            if not jobs:
                break

            total_pages = payload.get("total_pages", 1)

            for item in jobs:
                if self.limit and count >= self.limit:
                    return

                job_id = item.get("id")

                # Title
                title = (
                    clean_text(item.get("title") or "")
                    or clean_text((item.get("job_position") or {}).get("position_name") or "")
                )
                if not title:
                    continue

                # Company
                show_name = item.get("show_client_name", 0)
                client = item.get("client") or {}
                company = clean_text(client.get("client_name") or "") if show_name != 0 else "Confidential"
                if not company or company == "Confidential":
                    company = "Confidential Employer"

                # Location
                addresses = item.get("job_addresses") or []
                locs = [clean_text(a.get("sub_location") or "") for a in addresses if a.get("sub_location")]
                location = ", ".join(locs) if locs else ""

                # Deadline
                deadline = parse_date(item.get("dead_line"))

                # Description from job_duties
                duties = item.get("job_duties") or {}
                desc_html = (
                    (duties.get("main_duties") or "")
                    + (duties.get("qualification") or "")
                )

                # Apply URL
                ext_url = item.get("job_external_url")
                email = item.get("job_email")
                if ext_url:
                    apply_url = ext_url
                elif email:
                    apply_url = f"mailto:{email}"
                else:
                    apply_url = f"{PORTAL_URL}/jobs/{job_id}" if job_id else PORTAL_URL

                yield NormalizedJob(
                    source=self.key,
                    title=title,
                    organization=company,
                    location=location,
                    deadline=deadline,
                    description=desc_html,
                    apply_url=apply_url,
                    source_url=f"{PORTAL_URL}/jobs/{job_id}" if job_id else PORTAL_URL,
                    external_id=f"ekazi:{job_id}" if job_id else "",
                )
                count += 1

            page += 1
            if page > total_pages:
                break

