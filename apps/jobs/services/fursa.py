"""Fursa Tanzania – https://fursa.co.tz/job-listings/

Fursa is a WordPress site running the WP Job Manager plugin.
That plugin exposes a clean REST endpoint at:
    /wp-json/wp/v2/job-listings

Each record contains:
    id, slug, link, date, title.rendered,
    content.rendered (full job description as HTML),
    meta._job_location, meta._application (apply URL or email),
         meta._company_name, meta._company_website

No Playwright needed — plain requests work perfectly.

PAGINATION: WP REST API uses the X-WP-TotalPages response header.
We walk pages up to MAX_PAGES or self.limit, whichever stops first.
"""
from __future__ import annotations

import logging
import re
from typing import Iterator

from .base import BaseScraper, NormalizedJob, clean_text, make_external_id, parse_date

log = logging.getLogger("jobs.scrapers")

BASE_URL = "https://fursa.co.tz"
API_ENDPOINT = f"{BASE_URL}/wp-json/wp/v2/job-listings"
LISTING_PAGE = f"{BASE_URL}/job-listings/"
MAX_PAGES = 10          # ~18 jobs/page → 180 jobs max per run (tweak freely)
PER_PAGE = 18           # matches what the site itself uses


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _extract_deadline(html_body: str) -> str | None:
    """Pull the first date-looking phrase after keywords like 'deadline', 'closing date'."""
    pattern = re.compile(
        r"(?:application\s+)?(?:deadline|closing\s+date|close\s+date|due\s+date)"
        r"\s*[:\-–]\s*"
        r"([A-Za-z]+\s+\d{1,2}[,\s]+\d{4}|\d{1,2}[\s/-][A-Za-z]+[\s/-]\d{4}|\d{4}-\d{2}-\d{2})",
        re.I,
    )
    # Strip tags for clean matching
    text = re.sub(r"<[^>]+>", " ", html_body)
    m = pattern.search(text)
    return m.group(1) if m else None


def _resolve_apply_url(meta: dict, job_link: str) -> str:
    """Return a real apply URL: prefer _application if it looks like a URL, else job link."""
    raw = (meta.get("_application") or "").strip()
    if raw.startswith("http"):
        return raw
    # email → link to the job post so the user can copy the address from the description
    return job_link


class FursaTanzaniaScraper(BaseScraper):
    """Scrapes all active job-listings from fursa.co.tz via the WP REST API."""

    key = "fursa_tz"
    source_name = "Fursa Tanzania"
    db_source = "api"   # it's an aggregator board
    respect_robots = True

    def fetch(self) -> Iterator[NormalizedJob]:
        page = 1
        seen = 0
        while page <= MAX_PAGES:
            params = {
                "per_page": PER_PAGE,
                "page": page,
                "_fields": "id,slug,link,date,title,content,meta",
                "status": "publish",
            }
            try:
                resp = self.get(API_ENDPOINT, params=params)
            except Exception as exc:
                log.warning("[%s] page %d fetch failed: %s", self.key, page, exc)
                break

            records = resp.json()
            if not records:
                break

            total_pages = int(resp.headers.get("X-WP-TotalPages", 1))

            for rec in records:
                meta = rec.get("meta") or {}
                title = clean_text((rec.get("title") or {}).get("rendered", ""))
                company = clean_text(meta.get("_company_name", "") or "Fursa Tanzania")
                location = clean_text(meta.get("_job_location", ""))
                job_link = rec.get("link", LISTING_PAGE)
                content_html = (rec.get("content") or {}).get("rendered", "")
                apply_url = _resolve_apply_url(meta, job_link)
                deadline_str = _extract_deadline(content_html)
                ext_id = f"fursa:{rec['id']}"

                yield NormalizedJob(
                    source=self.key,
                    title=title,
                    organization=company,
                    location=location,
                    deadline=parse_date(deadline_str),
                    description=content_html,
                    apply_url=apply_url,
                    source_url=job_link,
                    external_id=make_external_id(self.key, str(rec["id"])),
                )
                seen += 1
                if self.limit and seen >= self.limit:
                    return

            if page >= total_pages:
                break
            page += 1
