from firecrawl import Firecrawl
from pydantic import BaseModel
from django.conf import settings

class JobOut(BaseModel):
    title: str
    organization: str | None = None
    location: str | None = None
    deadline: str | None = None        # YYYY-MM-DD
    description: str | None = None
    apply_url: str | None = None

class JobsPage(BaseModel):
    jobs: list[JobOut]

PROMPT = (
    "Extract every job posting found on this page. Never invent or hallucinate information. "
    "For each job, extract: title, organization (company name), location, deadline (format YYYY-MM-DD if available), "
    "description, and the exact apply_url from the page's apply links. "
    "Missing field = null. If there are no jobs on the page, return an empty list."
   
)

def get_firecrawl_client():
    api_key = getattr(settings, "FIRECRAWL_API_KEY", None)
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY is not set in settings or .env")
    return Firecrawl(api_key=api_key)

def scrape_jobs(url):
    fc = get_firecrawl_client()
    doc = fc.scrape(
        url,
        formats=[
            {"type": "json", "schema": JobsPage.model_json_schema(), "prompt": PROMPT},
            "links",
        ],
    )
    data = doc.json or {}
    return data.get("jobs", []), list(doc.links or [])

