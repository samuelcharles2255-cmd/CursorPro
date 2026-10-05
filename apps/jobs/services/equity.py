"""Equity Bank Tanzania - https://equitygroupholdings.com/tz/careers

Verified against the live page: server-rendered. Each vacancy is
    "Oct 02 2026"  ->  <h5>Title</h5>  ->  short blurb  ->  [View Details] link to a PDF job description

Facts you must know:
  * The page has NO per-job location (only a 'Head Office' filter label), so location = 'Head Office'.
  * 'View Details' is a PDF JD (some are access-protected), not an application page.
    Equity's own job ads say to apply by email, so apply_url is a mailto: link. VERIFY the address
    against a current JD before shipping - it comes from ads, not from this page.
  * The page contained a typo'd deadline (year 2028). The normalizer drops deadlines >400 days out.
"""
import re
from typing import Iterator
from urllib.parse import quote, urljoin

from .base import BaseScraper, NormalizedJob, clean_text

URL = "https://equitygroupholdings.com/tz/careers"
APPLY_EMAIL = "TZRecruitment@equitybank.co.tz"
_DATE = re.compile(r"\b[A-Z][a-z]{2}\s+\d{1,2}\s+\d{4}\b")


class EquityScraper(BaseScraper):
    key = "equity"
    source_name = "Equity Bank Tanzania Careers"
    company_name = "Equity Bank Tanzania"

    def fetch(self) -> Iterator[NormalizedJob]:
        yield from self.parse(self.soup(URL))

    def parse(self, soup) -> Iterator[NormalizedJob]:
        for h in soup.find_all("h5"):
            title = clean_text(h.get_text())
            if not title:
                continue

            deadline = None  # date sits just before the title; stop if we cross another heading
            for s in h.find_all_previous(string=True, limit=8):
                if s.parent.name == "h5":
                    break
                m = _DATE.search(s)
                if m:
                    deadline = m.group(0)
                    break

            blurb, pdf = "", ""
            for el in h.next_elements:
                if getattr(el, "name", None) == "h5" and el is not h:
                    break
                name = getattr(el, "name", None)
                if name == "p" and not blurb:
                    blurb = clean_text(el.get_text(" "))
                if name == "a" and el.get("href") and not pdf:
                    pdf = urljoin(URL, el["href"])
                if blurb and pdf:
                    break

            if not (blurb or pdf):  # an h5 that is not a vacancy
                continue

            description = blurb + (f"\n\nFull job description (PDF): {pdf}" if pdf else "")
            yield NormalizedJob(
                source=self.key,
                title=title,
                organization=self.company_name,
                location="Head Office",
                deadline=deadline,
                description=description,
                apply_url=f"mailto:{APPLY_EMAIL}?subject={quote(title)}",
                source_url=URL,
            )
