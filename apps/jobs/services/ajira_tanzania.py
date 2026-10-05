"""Standalone helper for the Ajira Portal (portal.ajira.go.tz).

NOTE: The portal is JavaScript-rendered, so plain `requests` only returns
an empty HTML shell. This module works only if the portal happens to serve
a server-rendered fallback for simple GETs (rare). For reliable scraping
use `AjiraPortalScraper` in browser.py, which loads the page with Playwright.

This file is kept as a lightweight diagnostic/debug tool. Run it directly
to verify whether the portal is currently returning server-rendered HTML.
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://portal.ajira.go.tz"
VACANCIES_URL = f"{BASE_URL}/vacancies"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SuperAppJobsBot/1.0; +https://example.com/bot)",
}


def get_vacancies_page() -> str:
    response = requests.get(VACANCIES_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def get_vacancy_links() -> list:
    """Return all unique /view-advert/ URLs found on the vacancies listing page."""
    html = get_vacancies_page()
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "/view-advert/" in href:
            full_url = urljoin(BASE_URL, href)
            if full_url not in links:
                links.append(full_url)
    return links


def get_vacancy_details(url: str) -> dict:
    """Fetch a single vacancy page and return its raw text."""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return {
        "url": url,
        "raw_text": soup.get_text("\n", strip=True),
    }


if __name__ == "__main__":
    links = get_vacancy_links()
    print(f"Found {len(links)} vacancies")
    for link in links:
        print(link)

    for link in links[:3]:
        job = get_vacancy_details(link)
        print("=" * 80)
        print(job["raw_text"])