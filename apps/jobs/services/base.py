"""Shared plumbing for every job scraper: normalizers, the NormalizedJob record,
a polite HTTP client (robots.txt, delay, retries) and JSON-LD helpers."""
from __future__ import annotations

import hashlib
import html
import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Iterator, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

log = logging.getLogger("jobs.scrapers")

USER_AGENT = "Mozilla/5.0 (compatible; SuperAppJobsBot/1.0; +https://example.com/bot)"  # put your real URL here
MAX_DEADLINE_FUTURE_DAYS = 400  # anything further out is almost certainly a typo on the source site


# --------------------------------------------------------------------------- #
# Normalizers
# --------------------------------------------------------------------------- #
_WS = re.compile(r"[ \t\r\f\v\u00a0]+")


def clean_text(value) -> str:
    """Single-line text: strips tags, unescapes entities, collapses whitespace."""
    if value is None:
        return ""
    text = str(value)
    if "<" in text and ">" in text:
        text = BeautifulSoup(text, "html.parser").get_text(" ")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def clean_multiline(value) -> str:
    """Keeps paragraph/line structure but removes tags, junk spaces and repeated blank lines."""
    if not value:
        return ""
    text = str(value)
    if "<" in text and ">" in text:
        soup = BeautifulSoup(text, "html.parser")
        for br in soup.find_all("br"):
            br.replace_with("\n")
        for li in soup.find_all("li"):
            li.insert(0, "- ")
        for blk in soup.find_all(["p", "div", "li", "ul", "ol", "tr", "h1", "h2", "h3", "h4", "h5", "h6"]):
            blk.append("\n")  # only block-level tags break lines; inline <b>/<a> must not split words
        text = soup.get_text("")
    text = html.unescape(text)
    out, blank = [], False
    for line in (_WS.sub(" ", ln).strip() for ln in text.splitlines()):
        if line:
            out.append(line)
            blank = False
        elif out and not blank:
            out.append("")
            blank = True
    return "\n".join(out).strip()


_DATE_FORMATS = (
    "%d-%b-%Y", "%d-%B-%Y", "%b %d %Y", "%B %d %Y", "%b %d, %Y", "%B %d, %Y",
    "%d %b %Y", "%d %B %Y", "%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y", "%d-%m-%Y",
)
_ORDINAL = re.compile(r"(?<=\d)(st|nd|rd|th)\b", re.I)
_WEEKDAY = re.compile(r"^(mon|tue|wed|thu|fri|sat|sun)[a-z]*\.?,?\s+", re.I)


def parse_date(value) -> Optional[date]:
    """Parses the date formats Tanzanian sites actually use. Numeric dates are read day-first (dd/mm/yyyy)."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)) and value > 10**9:  # epoch seconds or milliseconds
        return date.fromtimestamp(value / 1000 if value > 10**11 else value)
    s = clean_text(value)
    if not s:
        return None
    iso = re.match(r"(\d{4}-\d{2}-\d{2})", s)  # also covers 2026-08-13T00:00:00Z
    if iso:
        try:
            return datetime.strptime(iso.group(1), "%Y-%m-%d").date()
        except ValueError:
            return None
    s = _WEEKDAY.sub("", s)
    s = _ORDINAL.sub("", s).replace(" of ", " ").replace("Sept", "Sep")
    s = re.sub(r"\s+", " ", s).strip(" .")
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


_CITIES = {
    "dar es salaam": "Dar es Salaam", "dar": "Dar es Salaam", "dsm": "Dar es Salaam",
    "dodoma": "Dodoma", "arusha": "Arusha", "mwanza": "Mwanza", "mbeya": "Mbeya",
    "zanzibar": "Zanzibar", "unguja": "Zanzibar", "tanga": "Tanga", "moshi": "Moshi",
    "morogoro": "Morogoro", "mtwara": "Mtwara", "iringa": "Iringa", "kigoma": "Kigoma",
    "tabora": "Tabora", "singida": "Singida", "songea": "Songea", "lindi": "Lindi",
}


def normalize_location(value) -> str:
    """'Dar Es-Salaam' -> 'Dar es Salaam, Tanzania'. Empty -> 'Tanzania'."""
    s = clean_text(value)
    if not s:
        return "Tanzania"
    s = re.sub(r"\bTZ\b|united republic of tanzania|tanzania,? united republic of", "Tanzania", s, flags=re.I)
    parts, seen = [], set()
    for raw in re.split(r"[;,/|]", s):
        p = raw.strip()
        if not p:
            continue
        key = re.sub(r"\s+", " ", p.lower().replace("-", " "))
        p = _CITIES.get(key) or (p.title() if p.islower() or p.isupper() else p)
        if p.lower() not in seen:
            seen.add(p.lower())
            parts.append(p)
    if "tanzania" not in seen:
        parts.append("Tanzania")
    return ", ".join(parts)


def make_external_id(*parts: str) -> str:
    return hashlib.sha1("|".join(clean_text(p).casefold() for p in parts).encode()).hexdigest()[:20]


# --------------------------------------------------------------------------- #
# The one record every scraper must produce
# --------------------------------------------------------------------------- #
@dataclass
class NormalizedJob:
    source: str                 # scraper key, e.g. "nmb"
    title: str
    organization: str
    location: str = ""
    deadline: Optional[date] = None
    description: str = ""
    apply_url: str = ""         # where the user taps through to apply
    source_url: str = ""        # the page the job was found on
    external_id: str = ""       # stable id used to upsert; generated if the source has none
    warnings: list = field(default_factory=list)

    def finalize(self) -> "NormalizedJob":
        today = date.today()
        self.title = clean_text(self.title)
        self.organization = clean_text(self.organization)
        self.location = normalize_location(self.location)
        self.description = clean_multiline(self.description)
        self.deadline = parse_date(self.deadline)
        if self.deadline and self.deadline > today + timedelta(days=MAX_DEADLINE_FUTURE_DAYS):
            self.warnings.append(f"deadline {self.deadline} is implausibly far away - dropped")
            self.deadline = None
        self.source_url = (self.source_url or "").strip()
        self.apply_url = (self.apply_url or self.source_url).strip()
        if not self.external_id:
            self.external_id = make_external_id(self.source, self.organization, self.title, self.location)
        return self

    @property
    def expired(self) -> bool:
        return self.deadline is not None and self.deadline < date.today()

    def problems(self) -> list:
        return [n for n in ("title", "organization", "apply_url") if not getattr(self, n)]


# --------------------------------------------------------------------------- #
# Base scraper (plain HTTP)
# --------------------------------------------------------------------------- #
class BaseScraper:
    key = ""
    source_name = ""
    company_name: Optional[str] = None   # set for single-employer scrapers; None for job boards
    respect_robots = True
    # The value written to Job.source in the database.
    # Must be one of Job.SOURCE_CHOICES: "api", "career_page", or "direct".
    # Override in subclasses if the source is an aggregator/API board (use "api").
    db_source = "career_page"

    def __init__(self, limit=None, delay=1.0, timeout=25, include_expired=False, debug_dir=None):
        self.limit, self.delay, self.timeout = limit, delay, timeout
        self.include_expired, self.debug_dir = include_expired, debug_dir
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en"})
        self._robots, self._last = {}, 0.0
        self.stats = {"seen": 0, "skipped_invalid": 0, "expired": 0, "duplicates": 0}

    # -- HTTP --------------------------------------------------------------
    def _allowed(self, url: str) -> bool:
        u = urlparse(url)
        base = f"{u.scheme}://{u.netloc}"
        rp = self._robots.get(base)
        if rp is None:
            rp = RobotFileParser()
            try:
                r = self.session.get(base + "/robots.txt", timeout=10)
                rp.parse(r.text.splitlines() if r.status_code == 200 else [])
            except requests.RequestException:
                rp.parse([])
            self._robots[base] = rp
        return rp.can_fetch(USER_AGENT, url)

    def get(self, url: str, **kw) -> requests.Response:
        if self.respect_robots and not self._allowed(url):
            raise PermissionError(f"robots.txt disallows {url}")
        for attempt in (1, 2, 3):
            pause = self.delay - (time.monotonic() - self._last)
            if pause > 0:
                time.sleep(pause)
            try:
                r = self.session.get(url, timeout=self.timeout, **kw)
                self._last = time.monotonic()
                if r.status_code in (429, 500, 502, 503, 504):
                    raise requests.HTTPError(f"HTTP {r.status_code}")
                r.raise_for_status()
                if not r.encoding or r.encoding.lower() == "iso-8859-1":
                    r.encoding = r.apparent_encoding
                return r
            except requests.RequestException as exc:
                resp = getattr(exc, "response", None)
                permanent = resp is not None and 400 <= resp.status_code < 500 and resp.status_code != 429
                if attempt == 3 or permanent:
                    raise
                time.sleep(2 ** attempt)

    def soup(self, url: str) -> BeautifulSoup:
        return BeautifulSoup(self.get(url).text, "html.parser")

    # -- contract ----------------------------------------------------------
    def fetch(self) -> Iterator[NormalizedJob]:
        raise NotImplementedError

    def scrape(self) -> list:
        out, seen = [], set()
        for raw in self.fetch():
            self.stats["seen"] += 1
            try:
                job = raw.finalize()
            except Exception:  # one bad record must not kill the run
                log.exception("[%s] could not normalize a record", self.key)
                self.stats["skipped_invalid"] += 1
                continue
            for w in job.warnings:
                log.warning("[%s] %s: %s", self.key, job.title, w)
            if job.problems():
                log.warning("[%s] skipped %r - missing %s", self.key, job.title or job.source_url, job.problems())
                self.stats["skipped_invalid"] += 1
                continue
            if job.expired and not self.include_expired:
                self.stats["expired"] += 1
                continue
            if job.external_id in seen:
                self.stats["duplicates"] += 1
                continue
            seen.add(job.external_id)
            out.append(job)
            if self.limit and len(out) >= self.limit:
                break
        return out


# --------------------------------------------------------------------------- #
# schema.org JobPosting (JSON-LD) helpers - most job boards emit this for Google for Jobs
# --------------------------------------------------------------------------- #
def _walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)


def extract_jobposting_jsonld(soup: BeautifulSoup) -> Optional[dict]:
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or tag.get_text() or "")
        except (ValueError, TypeError):
            continue
        for node in _walk(data):
            t = node.get("@type")
            if t == "JobPosting" or (isinstance(t, list) and "JobPosting" in t):
                return node
    return None


def _jsonld_location(node: dict) -> str:
    loc = node.get("jobLocation")
    locs = loc if isinstance(loc, list) else [loc]
    bits = []
    for item in locs:
        addr = (item or {}).get("address") if isinstance(item, dict) else None
        if isinstance(addr, dict):
            for k in ("addressLocality", "addressRegion", "addressCountry"):
                v = addr.get(k)
                v = v.get("name") if isinstance(v, dict) else v
                if v:
                    bits.append(str(v))
        elif isinstance(addr, str):
            bits.append(addr)
    if not bits and node.get("applicantLocationRequirements"):
        bits.append("Remote")
    return ", ".join(dict.fromkeys(bits))


def jobposting_to_normalized(node: dict, source: str, page_url: str) -> NormalizedJob:
    org = node.get("hiringOrganization")
    org = org.get("name") if isinstance(org, dict) else org
    return NormalizedJob(
        source=source,
        title=node.get("title", ""),
        organization=org or "",
        location=_jsonld_location(node),
        deadline=node.get("validThrough"),
        description=node.get("description", ""),
        apply_url=node.get("url") or page_url,
        source_url=page_url,
    )
