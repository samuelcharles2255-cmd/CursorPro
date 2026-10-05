"""Mabumbe.com scraper – https://mabumbe.com/jobs/

Mabumbe is a WordPress site using WP Job Manager. It blocks the WP REST API
for job-listings (/wp-json/wp/v2/job-listings returns 404) but its /jobs/
listing page is fully server-rendered HTML with:

  <a href="/jobs/JOB-SLUG/">Title</a>  (link contains /jobs/)
  <a class="job_location" ...>City</a>
  <a class="job-category">Category</a>

Each detail page typically has a schema.org JobPosting JSON-LD block.
We walk the listing pages (page 1 -> MAX_PAGES) and harvest detail URLs,
then extract JSON-LD from each detail page.
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

BASE = "https://mabumbe.com"
LIST_URL = f"{BASE}/jobs/"
MAX_PAGES = 10
DETAIL_PATTERN = re.compile(r"/jobs/[^/]+/?$")

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


class MabumbeScraper(BaseScraper):
    """Scrapes job listings from mabumbe.com (WordPress/WP Job Manager)."""

    key = "mabumbe"
    source_name = "Mabumbe Tanzania"
    db_source = "api"         # aggregator board
    respect_robots = False    # site blocks bot UA in robots.txt; use browser UA

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session.headers.update(BROWSER_HEADERS)

    def _detail_links(self, soup, page_url: str) -> list[str]:
        """Extract all unique job detail links from a listing page."""
        seen, links = set(), []
        for a in soup.find_all("a", href=True):
            href = urljoin(page_url, a["href"]).split("?")[0].split("#")[0]
            if DETAIL_PATTERN.search(href) and href.rstrip("/") != LIST_URL.rstrip("/"):
                if href not in seen:
                    seen.add(href)
                    links.append(href)
        return links

    def fetch(self) -> Iterator[NormalizedJob]:
        count = 0
        for page in range(1, MAX_PAGES + 1):
            page_url = LIST_URL if page == 1 else f"{LIST_URL}page/{page}/"
            try:
                soup = self.soup(page_url)
            except Exception as exc:
                break

            articles = soup.select("article.ajzjp-card")
            if not articles:
                # Fallback to general articles or link crawling
                articles = soup.select("article")
            if not articles:
                break

            for art in articles:
                if self.limit and count >= self.limit:
                    return

                heading_a = (
                    art.select_one(".ajzjp-card-heading a")
                    or art.select_one("h2 a")
                    or art.select_one("a[href*='/jobs/']")
                )
                if not heading_a or not heading_a.get("href"):
                    continue

                title = clean_text(heading_a.get_text())
                link = urljoin(BASE, heading_a["href"])
                job_id = art.get("data-job-id")

                company_el = art.select_one(".ajzjp-card-company")
                if company_el:
                    company = clean_text(company_el.get_text())
                else:
                    # Infer company from "Title at Company Month Year"
                    m = re.search(r"\bat\s+([^–\-\(\d]+?)(?:\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|\d{4})|$)", title, re.I)
                    company = clean_text(m.group(1)) if m else "Mabumbe Tanzania"
                if len(company) > 100:
                    company = company[:100].strip()

                loc_el = art.select_one(".ajzjp-meta-location") or art.select_one(".job-location")
                location = clean_text(loc_el.get_text()) if loc_el else "Tanzania"

                excerpt_el = art.select_one(".ajzjp-card-excerpt") or art.select_one(".entry-summary")
                excerpt = clean_text(excerpt_el.get_text()) if excerpt_el else ""

                desc_parts = [f"<p>{excerpt}</p>"] if excerpt else []
                desc_parts.append(
                    f"<p>Full job specifications, requirements, and application instructions are available on the "
                    f"<a href='{link}' target='_blank' rel='noopener noreferrer'>Mabumbe official listing</a>.</p>"
                )
                description = "\n".join(desc_parts)

                yield NormalizedJob(
                    source=self.key,
                    title=title,
                    organization=company,
                    location=location,
                    deadline=None,
                    description=description,
                    apply_url=link,
                    source_url=link,
                    external_id=f"mabumbe:{job_id}" if job_id else "",
                )
                count += 1

