"""CareerLink Africa scraper – https://www.careerlinkafrica.com/jobs

CareerLink Africa is a Next.js SSR site. The /jobs listing page is
server-rendered and includes a JSON-LD `ItemList` in `<head>` with
direct URLs to all featured job detail pages.

Each detail page has a `schema.org/JobPosting` JSON-LD block with full
structured data: title, hiringOrganization, jobLocation, validThrough,
description, and url.

Strategy:
  1. Fetch /jobs to get the ItemList JSON-LD → extract job detail URLs
  2. For each URL, fetch and parse the JobPosting JSON-LD
  3. Paginate via ?page=N or /jobs?page=N if a next link exists
"""
from __future__ import annotations

import json
import logging
import re
from typing import Iterator
from urllib.parse import urljoin, urlparse

from .base import (
    BaseScraper, NormalizedJob,
    extract_jobposting_jsonld, jobposting_to_normalized,
    clean_text,
)

log = logging.getLogger("jobs.scrapers")

BASE = "https://www.careerlinkafrica.com"
LIST_URL = f"{BASE}/jobs"
MAX_PAGES = 20

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
}

_JOB_PATH = re.compile(r"^/jobs/[^/]+/?$")


def _extract_itemlist_urls(soup) -> list[str]:
    """Parse ItemList JSON-LD from the page and return all job page URLs."""
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or tag.get_text() or "")
        except (ValueError, TypeError):
            continue
        if isinstance(data, dict) and data.get("@type") == "ItemList":
            items = data.get("itemListElement", [])
            return [item.get("url") for item in items if isinstance(item, dict) and item.get("url")]
        elif isinstance(data, list):
            for node in data:
                if isinstance(node, dict) and node.get("@type") == "ItemList":
                    items = node.get("itemListElement", [])
                    return [item.get("url") for item in items if isinstance(item, dict) and item.get("url")]
    return []


def _extract_detail_links(soup, page_url: str) -> list[str]:
    """Extract job detail links from anchor tags on the listing page."""
    links = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(page_url, a["href"]).split("?")[0].split("#")[0]
        path = urlparse(href).path
        if _JOB_PATH.match(path) and href not in seen:
            seen.add(href)
            links.append(href)
    return links


class CareerLinkAfricaScraper(BaseScraper):
    """Scrapes job listings from CareerLink Africa (Next.js SSR + JSON-LD)."""

    key = "careerlinkafrica"
    source_name = "CareerLink Africa"
    db_source = "api"
    respect_robots = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session.headers.update(BROWSER_HEADERS)

    def fetch(self) -> Iterator[NormalizedJob]:
        count = 0
        seen_urls: set[str] = set()

        for page in range(1, MAX_PAGES + 1):
            page_url = LIST_URL if page == 1 else f"{LIST_URL}?page={page}"
            try:
                soup = self.soup(page_url)
            except Exception as exc:
                log.warning("[careerlinkafrica] page %d failed: %s", page, exc)
                break

            # Try JSON-LD ItemList first
            urls = _extract_itemlist_urls(soup)
            # Also collect direct anchor links
            urls += _extract_detail_links(soup, page_url)
            urls = [u for u in urls if u and u not in seen_urls]
            if not urls:
                break

            for url in urls:
                if self.limit and count >= self.limit:
                    return
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                try:
                    detail = self.soup(url)
                except Exception as exc:
                    log.debug("[careerlinkafrica] detail %s failed: %s", url, exc)
                    continue

                node = extract_jobposting_jsonld(detail)
                if node:
                    yield jobposting_to_normalized(node, self.key, url)
                    count += 1
                else:
                    log.debug("[careerlinkafrica] no JSON-LD on %s", url)

            # Check for next page link
            next_el = soup.select_one("a[rel=next]") or soup.find("a", string=re.compile(r"Next", re.I))
            if not next_el:
                break

