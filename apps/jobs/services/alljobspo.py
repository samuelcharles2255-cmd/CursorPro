"""AllJobspo Tanzania scraper – https://jobsintanzania.alljobspo.com/jobs

AllJobspo serves fully server-rendered HTML. Job cards use:

  <article class="job">
    <h2 class="heading"><a href="/job-details/ID">Title</a></h2>
    <div class="attribute company"><span class="value">Category</span></div>
    <div class="attribute location">
      <span class="value">from SOURCE</span>
      <span class="value" data-value="...">Posted date</span>
    </div>
    <div class="summary"><p>Excerpt with category, deadline, location</p></div>
  </article>

Each detail page has schema.org JobPosting JSON-LD in <head>.
Pagination via ?start=20, ?start=40 (20 per page).
"""
from __future__ import annotations

import re
from typing import Iterator
from urllib.parse import urljoin

from .base import (
    BaseScraper, NormalizedJob,
    extract_jobposting_jsonld, jobposting_to_normalized,
    clean_text, parse_date,
)

BASE = "https://jobsintanzania.alljobspo.com"
LIST_URL = f"{BASE}/jobs"
PAGE_SIZE = 20
MAX_PAGES = 20

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
}

_DEADLINE_RE = re.compile(r"Deadline[^:]*:\s*([A-Za-z]+day,?\s+\w+\s+\d+\s+\d{4})", re.I)
_LOCATION_RE = re.compile(r"Duty Station:\s*([^|]+)", re.I)


class AllJobspoScraper(BaseScraper):
    """Scrapes job listings from AllJobspo Tanzania."""

    key = "alljobspo"
    source_name = "AllJobspo Tanzania"
    db_source = "api"
    respect_robots = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session.headers.update(BROWSER_HEADERS)

    def _parse_summary(self, text: str) -> dict:
        """Extract deadline and location from the job summary snippet."""
        result = {"deadline": None, "location": ""}
        m = _DEADLINE_RE.search(text)
        if m:
            result["deadline"] = parse_date(m.group(1).strip())
        m = _LOCATION_RE.search(text)
        if m:
            result["location"] = m.group(1).strip().split("|")[0].strip()
        return result

    def fetch(self) -> Iterator[NormalizedJob]:
        count = 0
        for page_idx in range(MAX_PAGES):
            start = page_idx * PAGE_SIZE
            url = LIST_URL if page_idx == 0 else f"{LIST_URL}?start={start}"
            try:
                soup = self.soup(url)
            except Exception:
                break

            articles = soup.select("article.job")
            if not articles:
                break

            for art in articles:
                if self.limit and count >= self.limit:
                    return

                # Extract link to detail page
                heading_a = art.select_one("h2.heading a")
                if not heading_a:
                    continue
                detail_url = urljoin(BASE, heading_a.get("href", ""))

                # Extract summary for location and deadline hints
                summary_el = art.select_one(".summary p")
                summary_text = clean_text(summary_el.get_text()) if summary_el else ""
                hints = self._parse_summary(summary_text)

                # Fetch detail page for JSON-LD
                try:
                    detail = self.soup(detail_url)
                except Exception:
                    continue

                node = extract_jobposting_jsonld(detail)
                if node:
                    job = jobposting_to_normalized(node, self.key, detail_url)
                    # Fill in missing data from summary
                    if not job.deadline and hints["deadline"]:
                        job.deadline = hints["deadline"]
                    if not job.location and hints["location"]:
                        job.location = hints["location"]
                    yield job
                else:
                    # Fallback: parse detail HTML directly
                    title_el = detail.select_one("h1") or detail.select_one(".job_title")
                    company_el = detail.select_one(".company") or detail.select_one('[class*="employer"]')
                    title = clean_text(title_el.get_text()) if title_el else clean_text(heading_a.get_text())
                    org = clean_text(company_el.get_text()) if company_el else "AllJobspo Tanzania"
                    desc_el = detail.select_one(".job_description") or detail.select_one('[class*="desc"]')
                    desc = str(desc_el) if desc_el else summary_text

                    if title:
                        yield NormalizedJob(
                            source=self.key,
                            title=title,
                            organization=org,
                            location=hints["location"],
                            deadline=hints["deadline"],
                            description=desc,
                            apply_url=detail_url,
                            source_url=detail_url,
                        )
                count += 1

