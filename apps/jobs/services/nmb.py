"""NMB Bank Plc - https://careers.nmbbank.co.tz/nmb_career/career.aspx

Verified against the live page: server-rendered ASP.NET DataList, all vacancies on one page.
Each vacancy reads:
    <Title> (N Position(s)) Job Location : X Job Purpose: ... Job opening date : dd-Mon-yyyy
    Job closing date : dd-Mon-yyyy   [Login to Apply]
The parser works on page TEXT, not CSS ids, so it survives markup changes.

Limits (cannot be fixed by scraping):
  * 'Login to Apply' is an ASP.NET __doPostBack button. There is no per-job URL, so apply_url is the
    listing page and the user must log in there and pick the job again.
  * Some vacancies have no 'Job Location' - those become 'Tanzania'.
"""
import re
from typing import Iterator

from .base import BaseScraper, NormalizedJob, clean_text, make_external_id

URL = "https://careers.nmbbank.co.tz/nmb_career/career.aspx"

_TITLE = re.compile(r"(?P<title>.+?)\s*\(\s*\d+\s*Position\(s\)\s*\)")
_LOCATION = re.compile(r"Job Location\s*:\s*(?P<v>.*?)\s*(?:Job Purpose|Main Responsibilities)\s*:", re.S)
_OPEN = re.compile(r"Job opening date\s*:\s*(\d{1,2}-[A-Za-z]{3}-\d{4})")
_CLOSE = re.compile(r"Job closing date\s*:\s*(\d{1,2}-[A-Za-z]{3}-\d{4})")


class NMBScraper(BaseScraper):
    key = "nmb"
    source_name = "NMB Bank Careers"
    company_name = "NMB Bank Plc"

    def fetch(self) -> Iterator[NormalizedJob]:
        soup = self.soup(URL)
        yield from self.parse_text(soup.get_text("\n"))

    def parse_text(self, text: str) -> Iterator[NormalizedJob]:
        for chunk in re.split(r"Login to Apply", text):
            # Collapse whitespace first so all regexes operate on a clean line
            flat = re.sub(r"\s+", " ", chunk).strip()
            # Drop the page header that precedes the first vacancy (e.g. "Vacancies (3)")
            flat = re.sub(r"^.*?Vacancies\s*\(\d+\)\s*", "", flat).strip()

            m = _TITLE.match(flat)
            if not m:
                continue  # footer / no vacancy in this chunk

            title = clean_text(m.group("title"))
            loc = _LOCATION.search(flat)
            location = clean_text(loc.group("v")) if loc else ""
            closing = _CLOSE.search(flat)

            # Extract the body from the cleaned flat string, not from raw chunk
            start = flat.find("Job Purpose")
            end = flat.find("Job opening date")
            if start != -1:
                body = flat[start: end if end > start else None]
            else:
                body = ""

            yield NormalizedJob(
                source=self.key,
                title=title,
                organization=self.company_name,
                location=location,
                deadline=closing.group(1) if closing else None,
                description=body,
                apply_url=URL,
                source_url=URL,
                # title + location, NOT closing date: a re-posted role should update, not duplicate
                external_id=make_external_id(self.key, title, location),
            )

