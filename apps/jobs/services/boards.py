"""Job boards: BrighterMonday, Fuzu, Ajirika.

APPROACH: list page -> collect detail links -> read the schema.org JobPosting JSON-LD on each detail page.
Boards publish that markup so Google for Jobs can index them, which makes it far more stable than CSS
selectors. It yields title, organization, location, deadline (validThrough), description and url in one go.

HONEST STATUS - I could NOT load these sites from my environment, so the LIST URLs and LINK PATTERNS
below are educated guesses, not verified. First run:  --source brightermonday --limit 3 -v 2
If a board returns 0 jobs, either the link pattern is wrong or the detail pages carry no JSON-LD; the log
tells you which. Fix = edit LIST_URLS / LINK_PATTERN below. No other code needs to change.

LEGAL: these are commercial aggregators whose terms usually forbid scraping and republishing. Link out,
store short snippets, and get written permission before you launch. See the notes in the chat reply.
"""
import logging
import os
import re
from typing import Iterator
from urllib.parse import urljoin, urlparse

from .base import BaseScraper, NormalizedJob, extract_jobposting_jsonld, jobposting_to_normalized

log = logging.getLogger("jobs.scrapers")


class JsonLdBoardScraper(BaseScraper):
    LIST_URLS: list = []          # first page of each listing to crawl
    LINK_PATTERN = r"/jobs?/"     # regex a detail-page href must match
    PAGE_PARAM = "page"           # ?page=2 style pagination
    MAX_PAGES = 3

    def list_urls(self) -> list:
        return self.LIST_URLS

    def detail_links(self, soup, page_url) -> list:
        pat, host, links = re.compile(self.LINK_PATTERN), urlparse(page_url).netloc, []
        for a in soup.find_all("a", href=True):
            href = urljoin(page_url, a["href"]).split("#")[0]
            if urlparse(href).netloc == host and pat.search(urlparse(href).path) and href not in links \
                    and href.rstrip("/") != page_url.rstrip("/"):
                links.append(href)
        return links

    def fetch(self) -> Iterator[NormalizedJob]:
        urls = self.list_urls()
        if not urls:
            raise RuntimeError(f"{self.key}: no LIST_URLS configured")
        no_jsonld = 0
        for base_url in urls:
            for page in range(1, self.MAX_PAGES + 1):
                page_url = base_url if page == 1 else f"{base_url}{'&' if '?' in base_url else '?'}{self.PAGE_PARAM}={page}"
                links = self.detail_links(self.soup(page_url), page_url)
                log.info("[%s] %s -> %d detail links", self.key, page_url, len(links))
                if not links:
                    break
                for link in links:
                    try:
                        detail = self.soup(link)
                    except Exception as exc:
                        log.warning("[%s] detail fetch failed %s: %s", self.key, link, exc)
                        continue
                    node = extract_jobposting_jsonld(detail)
                    if not node:
                        no_jsonld += 1
                        log.warning("[%s] no JobPosting JSON-LD on %s", self.key, link)
                        continue
                    yield jobposting_to_normalized(node, self.key, link)
        if no_jsonld:
            log.warning("[%s] %d detail pages had no JSON-LD - the selectors/site changed or the page is JS-only", self.key, no_jsonld)


class BrighterMondayScraper(JsonLdBoardScraper):
    key = "brightermonday"
    source_name = "BrighterMonday Tanzania"
    LIST_URLS = ["https://www.brightermonday.co.tz/jobs"]      # UNVERIFIED
    LINK_PATTERN = r"^/listings?/"                              # UNVERIFIED


class FuzuScraper(JsonLdBoardScraper):
    key = "fuzu"
    source_name = "Fuzu Tanzania"
    LIST_URLS = ["https://www.fuzu.com/tanzania/job"]           # UNVERIFIED
    LINK_PATTERN = r"^/tanzania/job/[^/]+"                      # UNVERIFIED


class AjirikaScraper(JsonLdBoardScraper):
    """I could not identify 'ajirika' with confidence (search only surfaced ajiriwa.net, a different site).
    Give me the exact URL - or set AJIRIKA_LIST_URL in your environment - before using it."""
    key = "ajirika"
    source_name = "Ajirika"
    LINK_PATTERN = r"/jobs?/[^/]+"                              # UNVERIFIED

    def list_urls(self) -> list:
        url = os.environ.get("AJIRIKA_LIST_URL", "")
        if not url:
            raise RuntimeError("Set AJIRIKA_LIST_URL (the job-listing page of the site you mean by 'ajirika').")
        return [url]
