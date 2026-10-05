import logging

from django.core.management.base import BaseCommand

from apps.jobs.models import Company
from apps.jobs.services import SCRAPERS, sync_company_ats_jobs
from apps.jobs.services.persist import save_jobs

logger = logging.getLogger(__name__)

SAMPLE_COMPANIES = [
    {
        "name": "Stripe",
        "website": "https://stripe.com",
        "career_page": "https://stripe.com/jobs",
        "country": "United States",
        "ats_type": "greenhouse",
        "ats_identifier": "stripe",
        "career_url": "https://boards-api.greenhouse.io/v1/boards/stripe/jobs",
        "active": True,
    },
    {
        "name": "Figma",
        "website": "https://figma.com",
        "career_page": "https://figma.com/careers",
        "country": "United States",
        "ats_type": "greenhouse",
        "ats_identifier": "figma",
        "career_url": "https://boards-api.greenhouse.io/v1/boards/figma/jobs",
        "active": True,
    },
    {
        "name": "Lever Demo",
        "website": "https://lever.co",
        "career_page": "https://jobs.lever.co/leverdemo",
        "country": "United States",
        "ats_type": "lever",
        "ats_identifier": "leverdemo",
        "career_url": "https://jobs.lever.co/leverdemo",
        "active": True,
    },
    {
        "name": "Salesforce",
        "website": "https://salesforce.com",
        "career_page": "https://salesforce.wd12.myworkdayjobs.com/en-US/External_Career_Site",
        "country": "United States",
        "ats_type": "workday",
        "ats_identifier": "salesforce",
        "career_url": "https://salesforce.wd12.myworkdayjobs.com/en-US/External_Career_Site",
        "active": True,
    },
]

# ------------------------------------------------------------------
# The board/direct scrapers registered as permanent sources
# ------------------------------------------------------------------
SCRAPER_SOURCES = {
    "fursa_tz": {
        "label": "Fursa Tanzania (fursa.co.tz)",
        "description": "Plain-HTTP WP REST API scraper – no browser needed.",
    },
    "crdb_bank": {
        "label": "CRDB Bank Careers (careers.crdbbank.co.tz)",
        "description": "REST fast-path + Playwright fallback for the Next.js portal.",
    },
    "ekazi": {
        "label": "Ekazi Tanzania (ekazi.co.tz)",
        "description": "REST API scraper via api.ekazi.co.tz – no browser needed.",
    },
    "mabumbe": {
        "label": "Mabumbe Tanzania (mabumbe.com)",
        "description": "WordPress/WP Job Manager HTML scraper with JSON-LD fallback.",
    },
    "ajiramarket": {
        "label": "Ajira Market Tanzania (ajiramarket.co.tz)",
        "description": "Server-rendered HTML table scraper for ajiramarket.co.tz/vacancies.",
    },
    "alljobspo": {
        "label": "AllJobspo Tanzania (jobsintanzania.alljobspo.com)",
        "description": "HTML article + JSON-LD detail page scraper for AllJobspo Tanzania.",
    },
    "careerlinkafrica": {
        "label": "CareerLink Africa (careerlinkafrica.com)",
        "description": "Next.js SSR scraper – reads ItemList JSON-LD then per-job JobPosting JSON-LD.",
    },
    "eastworka": {
        "label": "EastWorka East Africa (eastworka.com)",
        "description": "React SPA sitemap-based scraper – reads job URLs from sitemap.xml.",
    },
    # Other SCRAPERS keys are also accepted via --source
}


def ensure_seed_companies():
    """Ensures at least one verified active company exists for Greenhouse, Lever, and Workday."""
    created_any = False
    for comp_data in SAMPLE_COMPANIES:
        comp, created = Company.objects.get_or_create(
            name=comp_data["name"],
            defaults=comp_data,
        )
        if not created and not comp.ats_type:
            comp.ats_type = comp_data["ats_type"]
            comp.ats_identifier = comp_data["ats_identifier"]
            comp.career_url = comp_data["career_url"]
            comp.active = True
            comp.save()
            created_any = True
        elif created:
            created_any = True
    return created_any


class Command(BaseCommand):
    help = (
        "Import jobs from company ATS platforms (Greenhouse, Lever, Workday) "
        "AND direct site scrapers (Fursa Tanzania, CRDB Bank, NMB, Equity ...)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--ats",
            type=str,
            choices=["greenhouse", "lever", "workday"],
            help="Filter ATS import to only this type.",
        )
        parser.add_argument(
            "--company",
            type=str,
            help="Filter ATS import to a specific company by name or ats_identifier.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum number of jobs to import per company / scraper.",
        )
        parser.add_argument(
            "--seed",
            action="store_true",
            help="Seed sample verified companies for Greenhouse, Lever, and Workday before running.",
        )
        parser.add_argument(
            "--source",
            type=str,
            metavar="KEY",
            help=(
                "Run a specific scraper by its key instead of (or in addition to) the ATS import. "
                f"Known scraper keys: {', '.join(sorted(SCRAPERS))}. "
                "Can be specified multiple times."
            ),
            action="append",
            dest="sources",
        )
        parser.add_argument(
            "--scrapers",
            action="store_true",
            help="Run ALL registered scrapers (Fursa, CRDB, NMB, Equity, ...) in addition to ATS.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and count jobs without writing to the database.",
        )
        parser.add_argument(
            "--debug-dump",
            type=str,
            metavar="DIR",
            default=None,
            dest="debug_dump",
            help="Directory to dump raw captured JSON (browser scrapers only). Useful for debugging.",
        )

    def handle(self, *args, **options):
        ats_filter = options.get("ats")
        company_filter = options.get("company")
        limit = options.get("limit")
        seed = options.get("seed")
        sources = options.get("sources") or []
        run_all_scrapers = options.get("scrapers", False)
        dry_run = options.get("dry_run", False)
        debug_dump = options.get("debug_dump")

        if dry_run:
            self.stdout.write(self.style.NOTICE("DRY RUN – no database writes."))

        # ------------------------------------------------------------------ #
        # Step 1: Optional seeding of ATS companies
        # ------------------------------------------------------------------ #
        if seed:
            self.stdout.write(self.style.NOTICE(
                "Seeding default verified companies for Greenhouse, Lever, and Workday..."
            ))
            ensure_seed_companies()

        # ------------------------------------------------------------------ #
        # Step 2: Run specific or all scrapers
        # ------------------------------------------------------------------ #
        scraper_keys = list(sources)
        if run_all_scrapers:
            scraper_keys = list(SCRAPERS.keys())

        if scraper_keys:
            self._run_scrapers(scraper_keys, limit=limit, dry_run=dry_run, debug_dump=debug_dump)

        # ------------------------------------------------------------------ #
        # Step 3: ATS (Greenhouse / Lever / Workday) import
        # ------------------------------------------------------------------ #
        # Skip ATS import when the user only requested specific scrapers and
        # did not pass --ats or --company flags.
        run_ats = not sources or ats_filter or company_filter or run_all_scrapers

        if not run_ats:
            return

        companies = Company.objects.filter(active=True).exclude(ats_type="")

        # Auto-seed if nothing configured
        if not companies.exists() and not company_filter:
            self.stdout.write(self.style.NOTICE(
                "No active ATS companies found. "
                "Auto-seeding verified sample companies (Stripe, Figma, Lever Demo, Salesforce)..."
            ))
            ensure_seed_companies()
            companies = Company.objects.filter(active=True).exclude(ats_type="")

        if ats_filter:
            companies = companies.filter(ats_type=ats_filter.lower())

        if company_filter:
            from django.db.models import Q
            companies = companies.filter(
                Q(name__icontains=company_filter) | Q(ats_identifier__icontains=company_filter)
            )

        if not companies.exists():
            self.stdout.write(self.style.WARNING(
                "No matching active companies found with an ATS configured."
            ))
            return

        total_created = 0
        total_updated = 0

        for company in companies:
            self.stdout.write(f"Importing from {company.name} ({company.ats_type})...")

            try:
                created, updated = sync_company_ats_jobs(company, limit=limit)
                total_created += created
                total_updated += updated
                self.stdout.write(self.style.SUCCESS(
                    f"  -> {company.name}: {created} created, {updated} updated"
                ))
            except Exception as error:
                logger.exception("import_jobs failed for %s", company.name)
                self.stdout.write(self.style.ERROR(
                    f"  -> Failed for {company.name}: {error}"
                ))

        self.stdout.write(self.style.SUCCESS(
            f"\nATS done! Total: {total_created} created, {total_updated} updated."
        ))

    # ---------------------------------------------------------------------- #
    # Scraper runner
    # ---------------------------------------------------------------------- #
    def _run_scrapers(self, keys: list[str], limit, dry_run: bool, debug_dump):
        self.stdout.write(self.style.NOTICE(
            f"\nRunning {len(keys)} scraper(s): {', '.join(keys)}"
        ))
        total_created = total_updated = 0

        for key in keys:
            scraper_cls = SCRAPERS.get(key)
            if scraper_cls is None:
                self.stdout.write(self.style.ERROR(
                    f"  Unknown scraper key '{key}'. "
                    f"Available: {', '.join(sorted(SCRAPERS))}"
                ))
                continue

            info = SCRAPER_SOURCES.get(key, {})
            label = info.get("label", scraper_cls.source_name or key)
            self.stdout.write(f"\nScraping {label}...")

            try:
                scraper = scraper_cls(limit=limit, debug_dir=debug_dump)
                jobs = scraper.scrape()
                stats = scraper.stats

                self.stdout.write(
                    f"  Parsed: {stats['seen']} seen, "
                    f"{stats.get('skipped_invalid', 0)} invalid, "
                    f"{stats.get('expired', 0)} expired, "
                    f"{stats.get('duplicates', 0)} duplicates -> {len(jobs)} valid."
                )

                if not jobs:
                    self.stdout.write(self.style.WARNING(f"  No jobs fetched for {key}."))
                    continue

                created, updated = save_jobs(
                    jobs,
                    dry_run=dry_run,
                    db_source=scraper.db_source,
                )
                total_created += created
                total_updated += updated
                self.stdout.write(self.style.SUCCESS(
                    f"  -> {label}: {created} created, {updated} updated"
                ))

            except PermissionError as exc:
                self.stdout.write(self.style.WARNING(f"  robots.txt blocked {key}: {exc}"))
            except Exception as exc:
                logger.exception("Scraper %s failed", key)
                self.stdout.write(self.style.ERROR(f"  -> Scraper '{key}' failed: {exc}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nScrapers done! Total: {total_created} created, {total_updated} updated."
        ))
