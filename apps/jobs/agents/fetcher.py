import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; YourSiteBot/1.0)"}

def fetch_html(url, needs_js=False):
    if needs_js:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=45000)
            html = page.content()
            browser.close()
            return html
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def clean_page(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "svg"]):
        tag.decompose()
    links = set()
    for a in soup.find_all("a", href=True):
        full = urljoin(base_url, a["href"])
        links.add(full)
        a.append(f" [LINK: {full}]")   # so Gemini sees which link belongs to which job
    return soup.get_text("\n", strip=True)[:60000], links