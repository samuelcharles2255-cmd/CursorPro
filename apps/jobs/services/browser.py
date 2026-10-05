"""JS-rendered sites: Ajira Portal, CRDB careers, Vodacom (via Vodafone's portal).

I fetched portal.ajira.go.tz/vacancies and careers.crdbbank.co.tz/jobs: both return an EMPTY HTML shell.
The jobs are loaded by JavaScript from a JSON API, so `requests` + BeautifulSoup can never work there.

APPROACH: open the page in headless Chromium, record every JSON response the page itself loads, find the
array that looks like a list of jobs, and map its keys to our fields using alias lists. This avoids guessing
CSS selectors I cannot see. It is HEURISTIC - run once with --debug-dump DIR, open the saved JSON, and if a
field is mapped wrong add the real key name to the alias tuples below (or hard-code the endpoint).

Setup:  pip install playwright && playwright install chromium
"""
import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterator
from urllib.parse import urljoin, urlparse

from .base import BaseScraper, NormalizedJob, clean_text

log = logging.getLogger("jobs.scrapers")


def _k(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(key).lower())


TITLE = tuple(map(_k, ("title", "jobTitle", "job_title", "positionTitle", "position", "vacancyTitle", "advertTitle", "designation", "postName")))
ORG = tuple(map(_k, ("organization", "organisation", "company", "companyName", "employer", "employerName", "institution", "institutionName", "agency", "department")))
LOCATION = tuple(map(_k, ("location", "jobLocation", "city", "region", "district", "dutyStation", "workLocation", "town")))
DEADLINE = tuple(map(_k, ("deadline", "closingDate", "closeDate", "expiryDate", "expiresAt", "endDate", "validThrough", "applicationDeadline", "dueDate", "lastDate")))
DESC = tuple(map(_k, ("description", "jobDescription", "summary", "purpose", "responsibilities", "details", "duties")))
URLK = tuple(map(_k, ("applyUrl", "applicationUrl", "url", "link", "jobUrl", "href")))
IDK = tuple(map(_k, ("id", "jobId", "vacancyId", "advertId", "reference", "referenceNumber", "slug", "uuid")))


def _unwrap(v):
    if isinstance(v, dict):
        for k in ("name", "title", "label", "value", "text"):
            if v.get(k):
                return _unwrap(v[k])
        return ""
    if isinstance(v, list):
        return ", ".join(x for x in (_unwrap(i) for i in v) if x)
    return v


def pick(rec: dict, aliases: tuple):
    norm = {_k(k): v for k, v in rec.items()}
    for a in aliases:
        v = _unwrap(norm.get(a))
        if v not in (None, "", []):
            return v
    return None


def find_lists(node, path=""):
    if isinstance(node, list):
        yield node
        for v in node:
            yield from find_lists(v, path)
    elif isinstance(node, dict):
        for v in node.values():
            yield from find_lists(v, path)


def looks_like_jobs(arr: list) -> bool:
    recs = [r for r in arr if isinstance(r, dict)]
    if not recs or len(recs) < 0.8 * len(arr):
        return False
    with_title = sum(1 for r in recs if pick(r, TITLE))
    if with_title / len(recs) < 0.7:
        return False
    extras = sum(1 for r in recs if any(pick(r, a) for a in (DEADLINE, LOCATION, ORG, IDK, URLK)))
    return extras / len(recs) >= 0.5


class BrowserJsonScraper(BaseScraper):
    START_URL = ""
    DEFAULT_ORG = ""                 # used when a record has no employer field
    FOLLOW_LINK_TEXT = None          # regex; if no jobs found, click the first matching link (Vodacom -> Vodafone)
    DETAIL_URL_TEMPLATE = None       # e.g. "https://.../vacancies/{id}" once you know it; else apply_url = listing page
    LOCATION_MUST_MATCH = None       # regex; drop records outside Tanzania on global portals
    SETTLE_MS = 5000
    SCROLLS = 6

    # -- browser -----------------------------------------------------------
    def _collect(self, page, payloads):
        def on_response(resp):
            try:
                if resp.status == 200 and "json" in (resp.headers.get("content-type") or ""):
                    payloads.append((resp.url, resp.json()))
            except Exception:
                pass
        page.on("response", on_response)

    def _load(self, page, url):
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(self.SETTLE_MS)
        for _ in range(self.SCROLLS):           # trigger lazy loading / infinite scroll
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(700)

    def _render(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError("pip install playwright && playwright install chromium") from exc
        payloads = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
                                       locale="en-US").new_page()
            self._collect(page, payloads)
            self._load(page, self.START_URL)
            if self.FOLLOW_LINK_TEXT and not self._best_records(payloads):
                link = page.get_by_role("link", name=re.compile(self.FOLLOW_LINK_TEXT, re.I)).first
                href = link.get_attribute("href") if link.count() else None
                if href:
                    log.info("[%s] following '%s' -> %s", self.key, self.FOLLOW_LINK_TEXT, urljoin(self.START_URL, href))
                    self._load(page, urljoin(self.START_URL, href))
            browser.close()
        return payloads

    # -- extraction --------------------------------------------------------
    def _best_records(self, payloads) -> list:
        groups = defaultdict(list)  # same endpoint (ignoring query string) => pages of the same list
        for url, data in payloads:
            for arr in find_lists(data):
                if looks_like_jobs(arr):
                    u = urlparse(url)
                    groups[f"{u.netloc}{u.path}"].extend(r for r in arr if isinstance(r, dict))
        return max(groups.values(), key=len) if groups else []

    def _dump(self, payloads):
        if not self.debug_dir:
            return
        d = Path(self.debug_dir)
        d.mkdir(parents=True, exist_ok=True)
        for i, (url, data) in enumerate(payloads):
            (d / f"{self.key}_{i:02d}.json").write_text(json.dumps({"url": url, "data": data}, indent=2, default=str)[:2_000_000])
        log.info("[%s] wrote %d captured JSON responses to %s", self.key, len(payloads), d)

    def fetch(self) -> Iterator[NormalizedJob]:
        payloads = self._render()
        self._dump(payloads)
        records = self._best_records(payloads)
        if not records:
            raise RuntimeError(
                f"[{self.key}] no job-like JSON captured from {len(payloads)} responses. Re-run with --debug-dump DIR, "
                "open DevTools > Network > Fetch/XHR on the site, find the jobs request, and add its key names "
                "to the alias tuples in browser.py."
            )
        must = re.compile(self.LOCATION_MUST_MATCH, re.I) if self.LOCATION_MUST_MATCH else None
        for rec in records:
            location = pick(rec, LOCATION) or ""
            if must and not must.search(f"{location} {pick(rec, DESC) or ''}"):
                continue
            rid = pick(rec, IDK)
            link = pick(rec, URLK)
            if link:
                url = urljoin(self.START_URL, str(link))
            elif rid and self.DETAIL_URL_TEMPLATE:
                url = self.DETAIL_URL_TEMPLATE.format(id=rid)
            else:
                url = self.START_URL
            yield NormalizedJob(
                source=self.key,
                title=pick(rec, TITLE) or "",
                organization=pick(rec, ORG) or self.DEFAULT_ORG,
                location=location,
                deadline=pick(rec, DEADLINE),
                description=pick(rec, DESC) or "",
                apply_url=url,
                source_url=self.START_URL,
                external_id=f"{self.key}:{rid}" if rid else "",
            )


class AjiraPortalScraper(BrowserJsonScraper):
    """Government recruitment portal (PSRS). Applying needs a portal login, so apply_url is the vacancy list
    unless you set DETAIL_URL_TEMPLATE after inspecting the API."""
    key = "ajira"
    source_name = "Ajira Portal (PSRS)"
    START_URL = "https://portal.ajira.go.tz/vacancies"
    DEFAULT_ORG = "Public Service Recruitment Secretariat (PSRS)"


class CRDBScraper(BrowserJsonScraper):
    key = "crdb"
    source_name = "CRDB Bank Careers"
    company_name = "CRDB Bank Plc"
    # The URL you gave (crdbbank.co.tz/jobs) is the marketing site. The recruitment portal is a separate host.
    START_URL = "https://careers.crdbbank.co.tz/jobs"
    DEFAULT_ORG = "CRDB Bank Plc"


class VodacomScraper(BrowserJsonScraper):
    """vodacom.com/search-jobs.php is only a landing page: it sends you to Vodafone's global careers portal.
    Least reliable scraper here - that portal lists ~3,000 jobs worldwide, hence the Tanzania filter."""
    key = "vodacom"
    source_name = "Vodacom Tanzania (via Vodafone careers)"
    company_name = "Vodacom Tanzania"
    START_URL = "https://www.vodacom.com/search-jobs.php"
    DEFAULT_ORG = "Vodacom Tanzania"
    FOLLOW_LINK_TEXT = r"vodafone career portal"
    LOCATION_MUST_MATCH = r"tanzania|dar es|arusha|mwanza|mbeya|dodoma|zanzibar|mtwara|moshi|morogoro|tanga"
