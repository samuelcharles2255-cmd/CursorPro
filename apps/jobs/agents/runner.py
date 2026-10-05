import os
import hashlib
from datetime import date, timedelta

# Auto-configure Django environment if executed directly as a script/module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
try:
    import django
    from django.apps import apps
    if not apps.ready:
        django.setup()
except Exception:
    pass

from django.utils import timezone
from .fetcher import fetch_html, clean_page
from .firecrawl_client import scrape_jobs
from apps.jobs.models import Company, Job, JobSource
from apps.jobs.services.persist import clean_company_name

def _parse_date(s):
    try:
        return date.fromisoformat(s) if s else None
    except ValueError:
        return None

def _norm(u):
    return (u or "").strip().rstrip("/")

def run_source(source):
    run_start = timezone.now()
    print(f"[*] Scraping source: {source.name} ({source.url})...")
    try:
        jobs, links = scrape_jobs(source.url)
        valid_links = {_norm(l) for l in links}
        print(f"    Fetched {len(jobs)} jobs, {len(links)} page links.")

        saved = 0
        for j in jobs:                       # j is now a dict, not an object
            apply_url = j.get("apply_url")
            if not apply_url or _norm(apply_url) not in valid_links:
                continue                     # kills hallucinated links
            deadline = _parse_date(j.get("deadline"))
            if deadline and deadline < date.today():
                continue
            fp = hashlib.sha256(
                f"{source.id}|{j['title']}|{j.get('organization')}|{apply_url}".encode()
            ).hexdigest()

            org_name = clean_company_name(j.get("organization") or "")
            company = None
            if org_name:
                company, _ = Company.objects.get_or_create(
                    name=org_name,
                    defaults={"country": j.get("location") or "Tanzania"},
                )

            Job.objects.update_or_create(
                fingerprint=fp,
                defaults=dict(
                    job_source=source,
                    company=company,
                    source=Job.SOURCE_DIRECT,
                    title=j["title"],
                    organization=org_name,
                    location=j.get("location") or "",
                    deadline=deadline,
                    description=j.get("description") or "",
                    application_url=apply_url,
                    last_seen=timezone.now(),
                    is_active=True,
                ),
            )
            saved += 1

        if saved > 0:
            Job.objects.filter(job_source=source, last_seen__lt=run_start).update(is_active=False)

        source.last_status = "ok" if saved else "zero_jobs"
        source.last_error = ""
        print(f"    [OK] Saved/updated {saved} jobs.")
    except Exception as e:
        source.last_status = "error"
        source.last_error = str(e)[:2000]
        print(f"    [ERROR] Failed: {e}")
    finally:
        source.last_run_at = timezone.now()
        source.save()

def run_all_due_sources():
    active_sources = list(JobSource.objects.filter(is_active=True))
    if not active_sources:
        print("[!] No active JobSource entries found in database. Add sources in Django Admin (/admin/jobs/jobsource/).")
        return

    due_count = 0
    for s in active_sources:
        if s.last_run_at and timezone.now() - s.last_run_at < timedelta(days=s.check_every_days, hours=-2):
            print(f"[-] Source {s.name} is not due yet (checked within {s.check_every_days} day(s)).")
            continue
        due_count += 1
        run_source(s)

    if due_count == 0:
        print("[i] All active sources have been checked recently and are not due yet.")

if __name__ == "__main__":
    run_all_due_sources()