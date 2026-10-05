"""Ajira Market Tanzania scraper – https://www.ajiramarket.co.tz/vacancies

Ajira Market is a Laravel/Alpine.js app. The /vacancies page is fully
server-rendered HTML. Job cards appear in an HTML table:

  <tr onclick="openJobDetailsModal('ID')">
    <td>...Title...</td>
    <td>...Company...</td>
    <td>...Location...</td>
    <td>...Close Date...</td>
  </tr>

Details are loaded via a modal (JavaScript), so we use the row data directly
and direct the user to the listing page for application. Pagination is via
?page=N query param.
"""
from __future__ import annotations

import re
from typing import Iterator

from .base import BaseScraper, NormalizedJob, clean_text, parse_date

BASE_URL = "https://www.ajiramarket.co.tz"
LIST_URL = f"{BASE_URL}/vacancies"
MAX_PAGES = 20

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
}

_ID_RE = re.compile(r"openJobDetailsModal\(['\"](\d+)['\"]\)")


class AjiraMarketScraper(BaseScraper):
    """Scrapes vacancies listed on ajiramarket.co.tz."""

    key = "ajiramarket"
    source_name = "Ajira Market Tanzania"
    db_source = "api"         # aggregator board
    respect_robots = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session.headers.update(BROWSER_HEADERS)

    def _parse_rows(self, soup) -> list[dict]:
        """Extract job rows from the table on the listing page."""
        rows = []
        for tr in soup.select("tr[onclick]"):
            onclick = tr.get("onclick", "")
            m = _ID_RE.search(onclick)
            job_id = m.group(1) if m else None

            cells = tr.find_all("td")
            if len(cells) < 4:
                continue

            # Title in cell[1], company in cell[2], location in cell[3], deadline in cell[4]
            title_el = cells[1].select_one("div.font-extrabold") or cells[1]
            company_el = cells[2].select_one("span.font-extrabold") or cells[2]
            location_el = cells[3].select_one("span") or cells[3]
            # deadline is in cell[4] if present
            deadline_el = cells[4] if len(cells) > 4 else None

            title = clean_text(title_el.get_text())
            company = clean_text(company_el.get_text())
            location = clean_text(location_el.get_text())
            deadline_str = clean_text(deadline_el.get_text()) if deadline_el else ""
            deadline = parse_date(deadline_str)

            if title and company:
                rows.append({
                    "id": job_id,
                    "title": title,
                    "company": company,
                    "location": location,
                    "deadline": deadline,
                })
        return rows

    def fetch(self) -> Iterator[NormalizedJob]:
        count = 0
        for page in range(1, MAX_PAGES + 1):
            url = LIST_URL if page == 1 else f"{LIST_URL}?page={page}"
            try:
                soup = self.soup(url)
            except Exception:
                break

            rows = self._parse_rows(soup)
            if not rows:
                break

            for row in rows:
                if self.limit and count >= self.limit:
                    return

                apply_url = f"{LIST_URL}"  # modal-only; link to listing page
                external_id = f"ajiramarket:{row['id']}" if row["id"] else None

                desc_parts = [
                    f"<p><strong>Position:</strong> {row['title']}</p>",
                    f"<p><strong>Employer:</strong> {row['company']}</p>",
                ]
                if row.get("location"):
                    desc_parts.append(f"<p><strong>Location:</strong> {row['location']}</p>")
                if row.get("deadline"):
                    desc_parts.append(f"<p><strong>Application Deadline:</strong> {row['deadline']}</p>")
                desc_parts.append(
                    "<p>This vacancy was published on Ajira Market Tanzania. "
                    f"To view complete requirements, documents, and submit your application, please visit the "
                    f"<a href='{LIST_URL}' target='_blank' rel='noopener noreferrer'>Ajira Market portal</a>.</p>"
                )
                description_html = "\n".join(desc_parts)

                yield NormalizedJob(
                    source=self.key,
                    title=row["title"],
                    organization=row["company"],
                    location=row["location"],
                    deadline=row["deadline"],
                    description=description_html,
                    apply_url=apply_url,
                    source_url=LIST_URL,
                    external_id=external_id or "",
                )
                count += 1

            # Check if there's a next page
            next_link = soup.select_one("a[rel=next]") or soup.select_one(".pagination .next")
            if not next_link:
                # Also check by detecting empty table
                break

