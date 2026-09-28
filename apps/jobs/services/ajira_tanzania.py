# jobs/services/ajira_tanzania.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://portal.ajira.go.tz"
VACANCIES_URL = f"{BASE_URL}/vacancies"


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_vacancies_page():
    response = requests.get(
        VACANCIES_URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text


def get_vacancy_links():
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


if __name__ == "__main__":
    links = get_vacancy_links()

    print(f"Found {len(links)} vacancies")

    for link in links:
        print(link)

def get_vacancy_details(url):

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text(
        "\n",
        strip=True
    )

    return {
        "url": url,
        "raw_text": text
    }
if __name__ == "__main__":

    links = get_vacancy_links()

    for link in links[:3]:

        job = get_vacancy_details(link)

        print("=" * 80)
        print(job["raw_text"])