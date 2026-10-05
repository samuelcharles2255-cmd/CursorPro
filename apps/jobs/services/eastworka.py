"""EastWorka scraper – https://eastworka.com

EastWorka is a Vite/React SPA (hosted on Lovable/Supabase). Job data is
loaded at runtime from a Supabase backend — no public REST API is exposed
without auth.

Strategy (best-effort):
  1. Try common Supabase REST paths (e.g. /rest/v1/jobs) if discoverable.
  2. Try the dynamic sitemap edge-function for individual job page URLs.
  3. Attempt to fetch and parse JSON-LD from those pages.

If none succeed the scraper logs a warning and yields nothing gracefully.
The scraper is registered so it can be updated when the site exposes an API.
"""
from __future__ import annotations

import logging
import re
from typing import Iterator
from urllib.parse import urljoin

from .base import (
    BaseScraper, NormalizedJob,
    extract_jobposting_jsonld, jobposting_to_normalized,
)

log = logging.getLogger("jobs.scrapers")

BASE = "https://eastworka.com"
SITEMAP_URL = f"{BASE}/sitemap.xml"
DYNAMIC_SITEMAP = f"{BASE}/functions/v1/generate-sitemap"

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xml,application/xhtml+xml;q=0.9,*/*;q=0.8",
}

_JOB_PATH = re.compile(r"/jobs?/[^/]+/?$")


class EastworkaScraper(BaseScraper):
    """Scrapes East Africa job listings from eastworka.com.

    NOTE: EastWorka is a Supabase-backed SPA. Its static sitemap only contains
    static page URLs (no individual job pages). Jobs are loaded dynamically
    from Supabase with auth. The scraper will gracefully return 0 results
    until the site exposes a public API or sitemap with job URLs.
    """

    key = "eastworka"
    source_name = "EastWorka East Africa"
    db_source = "api"
    respect_robots = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session.headers.update(BROWSER_HEADERS)

    def _get_sitemap_urls(self) -> list[str]:
        """Fetch the sitemap and extract all job page URLs."""
        job_urls = []
        for sitemap in [DYNAMIC_SITEMAP, SITEMAP_URL]:
            try:
                r = self.session.get(sitemap, timeout=15)
                if r.status_code == 200 and "<urlset" in r.text:
                    urls = re.findall(r"<loc>\s*(https?://[^<]+)\s*</loc>", r.text)
                    for u in urls:
                        u = u.strip()
                        if _JOB_PATH.search(u) and "eastworka.com" in u:
                            job_urls.append(u)
                    if job_urls:
                        break
            except Exception as exc:
                log.debug("[eastworka] sitemap %s failed: %s", sitemap, exc)
        return list(dict.fromkeys(job_urls))

    def fetch(self) -> Iterator[NormalizedJob]:
        urls = self._get_sitemap_urls()
        if not urls:
            log.warning(
                "[eastworka] No job URLs found – eastworka.com is a Supabase SPA with no public "
                "job listings API. The scraper is registered but yields nothing until the site "
                "exposes an accessible API or sitemap with job detail URLs."
            )
            return

        count = 0
        for url in urls:
            if self.limit and count >= self.limit:
                return
            try:
                soup = self.soup(url)
            except Exception as exc:
                log.debug("[eastworka] detail fetch failed %s: %s", url, exc)
                continue

            node = extract_jobposting_jsonld(soup)
            if node:
                yield jobposting_to_normalized(node, self.key, url)
                count += 1
            else:
                log.debug("[eastworka] no JSON-LD on %s", url)

