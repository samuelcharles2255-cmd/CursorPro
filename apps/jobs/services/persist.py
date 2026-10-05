"""Saves NormalizedJob records into your Django models.

I have NOT seen your Job model (only Company, via the command you pasted). So instead of hard-coding
field names, this module looks at the model's real concrete fields and maps each normalized attribute
to the first alias that exists. Anything the model cannot hold is reported ONCE per run - never silently
lost - so you can add the field or extend the alias lists below.

ASSUMPTIONS (change if wrong):
  * model `Job` lives in apps.jobs.models and has a FK to Company
  * Company.name is unique enough to look up by name
"""
import html
import logging
import re
from datetime import date, datetime

from django.db import transaction
from django.utils import timezone as dj_tz

from apps.jobs.models import Company, Job

log = logging.getLogger("jobs.scrapers")

# normalized attribute -> candidate model field names, in priority order
JOB_FIELD_ALIASES = {
    "title": ("title", "name"),
    "location": ("location", "city", "job_location"),
    # NormalizedJob.deadline is a date; the Job model stores it as expires_at (DateTimeField).
    # The mapping key is still "deadline" — we convert the value in save_jobs().
    "deadline": ("expires_at", "deadline", "closing_date", "application_deadline", "expiry_date", "valid_through"),
    "description": ("description", "details", "body"),
    # Job model uses application_url — keep apply_url first for any future migration
    "apply_url": ("application_url", "apply_url", "apply_link", "external_url", "url"),
    "source_url": ("source_url", "listing_url"),
    "source": ("source", "source_name", "platform"),
    # Job model uses source_job_id — must be in this list
    "external_id": ("source_job_id", "external_id", "source_id", "external_job_id"),
}
COMPANY_FK_ALIASES = ("company", "organization", "employer")

# Cached after first call — model introspection is cheap but pointless to repeat every sync.
# Reset to None to invalidate (e.g. in tests) by calling _reset_resolved_cache().
_RESOLVED: tuple | None = None


def _reset_resolved_cache():
    """Call this in tests after patching Job._meta or alias lists."""
    global _RESOLVED
    _RESOLVED = None


def model_fields(model) -> set:
    return {f.name for f in model._meta.get_fields() if getattr(f, "concrete", False)}


def filter_to_model(model, data: dict) -> dict:
    """Keep only keys that are real fields on `model`."""
    have = model_fields(model)
    return {k: v for k, v in data.items() if k in have}


def resolve_job_fields() -> tuple:
    global _RESOLVED
    if _RESOLVED is not None:
        return _RESOLVED
    have = model_fields(Job)
    mapping = {attr: next((n for n in names if n in have), None) for attr, names in JOB_FIELD_ALIASES.items()}
    fk = next((n for n in COMPANY_FK_ALIASES if n in have), None)
    _RESOLVED = mapping, fk
    return _RESOLVED


def clean_company_name(value) -> str:
    """Normalizes and sanitizes company/organization name.
    Strips HTML, collapses whitespace, removes navigational scraping debris,
    and caps length to avoid database pollution.
    """
    if not value:
        return "Tanzania Employer"
    text = str(value)
    if "<" in text and ">" in text:
        from bs4 import BeautifulSoup
        text = BeautifulSoup(text, "html.parser").get_text(" ")
    text = html.unescape(text)
    lower = text.lower()
    if "skip to content" in lower or ("menu" in lower and len(text) > 60):
        m = re.search(
            r"\bat\s+([^–\-\(\d\n]+?)(?:\s*[–\-]\s*(?:January|February|March|April|May|June|July|August|September|October|November|December|\d{4})|\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|\d{4})|$)",
            text,
            re.I,
        )
        if m:
            text = m.group(1).strip()
        else:
            text = re.sub(r"^(?:Skip to content|Menu|Home|Jobs).*?at\s+", "", text, flags=re.I)
    text = re.sub(r"\s*[–\-]\s*(?:January|February|March|April|May|June|July|August|September|October|November|December|\d{4}).*$", "", text, flags=re.I)
    text = re.sub(r"[\r\n\t]", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" .,–-")
    if len(text) > 100:
        text = text[:100].strip(" .,–-")
    return text or "Tanzania Employer"


def get_company(name: str, employer_company: Company = None) -> Company:
    """Employer scrapers pass their seeded Company. Job boards create/find one per organization."""
    if employer_company is not None:
        return employer_company
    clean_name = clean_company_name(name)
    existing = Company.objects.filter(name__iexact=clean_name).first()
    if existing:
        return existing
    defaults = filter_to_model(Company, {"name": clean_name, "country": "Tanzania", "active": True})
    return Company.objects.create(**defaults)


@transaction.atomic
def _upsert(model_cls, lookup, values):
    return model_cls.objects.update_or_create(**lookup, defaults=values)


def _coerce_deadline(value, field_name: str):
    """Convert a plain date to an aware datetime when the model field is a DateTimeField.

    Uses django.utils.timezone.make_aware so the project's TIME_ZONE setting is respected
    and Django does not emit a RuntimeWarning about naive datetimes.
    """
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        try:
            field = Job._meta.get_field(field_name)
            if field.get_internal_type() == "DateTimeField":
                return dj_tz.make_aware(datetime(value.year, value.month, value.day))
        except Exception:
            pass
    return value


def save_jobs(jobs, employer_company: Company = None, dry_run=False, db_source: str = None) -> tuple:
    """Returns (created, updated). Upsert key: (company, source, external_id) when the model has those fields,
    otherwise (company, title, apply_url).

    db_source: if provided, overrides job.source with this value (must be a valid Job.SOURCE_* choice,
    e.g. 'career_page', 'api', 'direct'). Use this to correct the scraper key ('nmb', 'equity') to a
    valid Job model source choice.
    """
    mapping, fk = resolve_job_fields()
    if not fk:
        raise RuntimeError("Job model has no FK to Company under any of %s" % (COMPANY_FK_ALIASES,))

    lost = [attr for attr in ("title", "apply_url") if not mapping[attr]]
    if lost:
        raise RuntimeError(f"Job model has no field for required attribute(s): {lost}. Extend JOB_FIELD_ALIASES.")
    not_stored = [attr for attr, field in mapping.items() if field is None]
    if not_stored:
        log.warning("Job model cannot store: %s (data is dropped, add fields to keep it)", ", ".join(not_stored))

    created = updated = 0
    for job in jobs:
        company = get_company(job.organization, employer_company)
        values = {}
        for attr, field_name in mapping.items():
            if field_name is None:
                continue
            raw = getattr(job, attr)
            # Convert date → datetime for DateTimeField columns (e.g. expires_at)
            values[field_name] = _coerce_deadline(raw, field_name) if attr == "deadline" else raw
        values[fk] = company

        # Override the DB source field with a valid Job.SOURCE_* choice if requested.
        # NormalizedJob.source is the scraper key ('nmb', 'equity') — useful for dedup,
        # but Job.source must be one of ('api', 'career_page', 'direct').
        effective_source = db_source or job.source
        if mapping["source"]:
            values[mapping["source"]] = effective_source

        # Ensure country is populated for filtering and search
        all_fields = model_fields(Job)
        if "country" in all_fields and not values.get("country"):
            loc_lower = (job.location or "").lower()
            if "tanzania" in loc_lower or "dar es salaam" in loc_lower or "dodoma" in loc_lower:
                values["country"] = "Tanzania"
            elif "kenya" in loc_lower or "nairobi" in loc_lower:
                values["country"] = "Kenya"
            elif "uganda" in loc_lower or "kampala" in loc_lower:
                values["country"] = "Uganda"
            elif "south africa" in loc_lower or "johannesburg" in loc_lower:
                values["country"] = "South Africa"
            elif "nigeria" in loc_lower or "lagos" in loc_lower:
                values["country"] = "Nigeria"
            elif company and getattr(company, "country", None):
                values["country"] = company.country
            else:
                values["country"] = "Tanzania"

        # Ensure posted_at is populated so scraped jobs sort to the top
        if "posted_at" in all_fields and not values.get("posted_at"):
            values["posted_at"] = dj_tz.now()

        if mapping["external_id"]:
            lookup = {fk: company, mapping["external_id"]: job.external_id}
            if mapping["source"]:
                lookup[mapping["source"]] = effective_source
        else:
            lookup = {fk: company, mapping["title"]: job.title, mapping["apply_url"]: job.apply_url}
        for k in lookup:
            values.pop(k, None)

        if dry_run:
            exists = Job.objects.filter(**lookup).exists()
            created += 0 if exists else 1
            updated += 1 if exists else 0
            continue
        _, was_created = _upsert(Job, lookup, values)
        created += was_created
        updated += not was_created
    return created, updated
