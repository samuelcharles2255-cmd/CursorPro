import logging

from apps.jobs.models import Job
from .greenhouse import (
    fetch_greenhouse_jobs,
    get_greenhouse_jobs,
    normalize_greenhouse_job,
)
from .lever import (
    fetch_lever_jobs,
    get_lever_jobs,
    normalize_lever_job,
)
from .workday import (
    fetch_workday_jobs,
    get_workday_jobs,
    normalize_workday_job,
    to_workday_cxs_url,
)
from .jooble import (
    fetch_jooble_jobs,
    sync_jooble_jobs,
)

logger = logging.getLogger(__name__)

__all__ = [
    "fetch_greenhouse_jobs",
    "get_greenhouse_jobs",
    "normalize_greenhouse_job",
    "fetch_lever_jobs",
    "get_lever_jobs",
    "normalize_lever_job",
    "fetch_workday_jobs",
    "get_workday_jobs",
    "normalize_workday_job",
    "to_workday_cxs_url",
    "fetch_jooble_jobs",
    "sync_jooble_jobs",
    "sync_company_ats_jobs",
    "sync_all_ats_jobs",
]


def sync_company_ats_jobs(company, limit=None):
    """
    Given a Company model instance, fetch jobs from its configured ATS
    (Greenhouse, Lever, or Workday) and upsert them into Job.

    Returns:
        tuple (created_count, updated_count)
    """
    ats_type = (company.ats_type or "").strip().lower()
    identifier = (company.ats_identifier or "").strip()
    career_url = (company.career_url or "").strip()

    if not ats_type:
        logger.warning("Company %s has no ats_type configured", company.name)
        return 0, 0

    if ats_type == "greenhouse":
        if not identifier:
            raise ValueError(f"Company {company.name} requires ats_identifier (e.g. 'stripe') for Greenhouse.")
        jobs = get_greenhouse_jobs(identifier, limit=limit)

    elif ats_type == "lever":
        if not identifier:
            raise ValueError(f"Company {company.name} requires ats_identifier (e.g. 'netflix') for Lever.")
        jobs = get_lever_jobs(identifier, limit=limit)

    elif ats_type == "workday":
        target_url = career_url or identifier
        if not target_url:
            raise ValueError(f"Company {company.name} requires career_url for Workday.")
        jobs = get_workday_jobs(api_url=target_url, limit=limit or 50)

    else:
        raise ValueError(f"Unsupported ATS type '{ats_type}' for {company.name}")

    created = 0
    updated = 0

    for job_data in jobs:
        source_job_id = job_data.get("source_job_id", "")
        title = job_data.get("title", "")

        if not source_job_id or not title:
            continue

        defaults = {
            "title": title,
            "company": company,
            "description": job_data.get("description", ""),
            "location": job_data.get("location", ""),
            "country": job_data.get("country", "") or company.country,
            "application_url": job_data.get("application_url", ""),
            "employment_type": job_data.get("employment_type", ""),
            "salary_min": job_data.get("salary_min"),
            "salary_max": job_data.get("salary_max"),
            "salary_currency": job_data.get("salary_currency", ""),
            "posted_at": job_data.get("posted_at"),
            "source": job_data.get("source", Job.SOURCE_CAREER_PAGE),
        }

        _, was_created = Job.objects.update_or_create(
            source=defaults["source"],
            source_job_id=source_job_id,
            defaults=defaults,
        )

        if was_created:
            created += 1
        else:
            updated += 1

    logger.info("Synced %s (%s): %d created, %d updated", company.name, ats_type, created, updated)
    return created, updated


def sync_all_ats_jobs(companies=None, limit=None):
    """
    Syncs jobs for all active companies with an ats_type configured, or for
    the provided queryset/list of companies.

    Returns:
        dict: Summary of results per company and totals
    """
    from apps.jobs.models import Company

    if companies is None:
        companies = Company.objects.filter(active=True).exclude(ats_type="")

    total_created = 0
    total_updated = 0
    results = {}

    for company in companies:
        try:
            created, updated = sync_company_ats_jobs(company, limit=limit)
            results[company.name] = {"created": created, "updated": updated, "error": None}
            total_created += created
            total_updated += updated
        except Exception as exc:
            logger.exception("Sync failed for %s", company.name)
            results[company.name] = {"created": 0, "updated": 0, "error": str(exc)}

    return {
        "results": results,
        "total_created": total_created,
        "total_updated": total_updated,
    }
