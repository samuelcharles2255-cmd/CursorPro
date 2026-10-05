"""scrape_jobs management command.

A thin wrapper around import_jobs that ONLY runs the direct site scrapers
(Fursa Tanzania, CRDB Bank, NMB, Equity, …) without touching the ATS pipeline.

Usage:
    # Run ALL registered scrapers
    python manage.py scrape_jobs

    # Run specific scrapers
    python manage.py scrape_jobs --source fursa_tz --source crdb_bank

    # Limit to 20 jobs per scraper, dry-run only
    python manage.py scrape_jobs --limit 20 --dry-run

    # Dump raw JSON payloads from browser scrapers for debugging
    python manage.py scrape_jobs --source crdb_bank --debug-dump /tmp/crdb_debug
"""
from django.core.management.base import BaseCommand

from apps.jobs.services import SCRAPERS
from apps.jobs.services.persist import save_jobs

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Run direct site scrapers (Fursa Tanzania, CRDB Bank, NMB, Equity, …) "
        "and save the results to the database."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=str,
            metavar="KEY",
            help=(
                f"Scraper key to run. Repeat for multiple. "
                f"Available: {', '.join(sorted(SCRAPERS))}. "
                "Default: all scrapers."
            ),
            action="append",
            dest="sources",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum number of jobs to scrape per source.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Count jobs without writing to the database.",
        )
        parser.add_argument(
            "--debug-dump",
            type=str,
            metavar="DIR",
            default=None,
            dest="debug_dump",
            help="Directory to save raw JSON payloads (browser scrapers only).",
        )

    def handle(self, *args, **options):
        keys = options.get("sources") or list(SCRAPERS.keys())
        limit = options.get("limit")
        dry_run = options.get("dry_run", False)
        debug_dump = options.get("debug_dump")

        if dry_run:
            self.stdout.write(self.style.NOTICE("DRY RUN - no database writes."))

        self.stdout.write(self.style.NOTICE(
            f"Running {len(keys)} scraper(s): {', '.join(keys)}"
        ))

        total_created = total_updated = 0

        for key in keys:
            cls = SCRAPERS.get(key)
            if not cls:
                self.stdout.write(self.style.ERROR(
                    f"Unknown scraper '{key}'. Available: {', '.join(sorted(SCRAPERS))}"
                ))
                continue

            self.stdout.write(f"\n[{key}] {cls.source_name or key} ...")
            try:
                scraper = cls(limit=limit, debug_dir=debug_dump)
                jobs = scraper.scrape()
                stats = scraper.stats
                self.stdout.write(
                    f"  {stats['seen']} seen, "
                    f"{stats.get('skipped_invalid', 0)} invalid, "
                    f"{stats.get('expired', 0)} expired -> {len(jobs)} valid."
                )
                if jobs:
                    created, updated = save_jobs(
                        jobs,
                        dry_run=dry_run,
                        db_source=scraper.db_source,
                    )
                    total_created += created
                    total_updated += updated
                    self.stdout.write(self.style.SUCCESS(
                        f"  Saved: {created} created, {updated} updated."
                    ))
                else:
                    self.stdout.write(self.style.WARNING(f"  No valid jobs found."))
            except PermissionError as exc:
                self.stdout.write(self.style.WARNING(f"  robots.txt blocked: {exc}"))
            except Exception as exc:
                logger.exception("Scraper %s failed", key)
                self.stdout.write(self.style.ERROR(f"  FAILED: {exc}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Total: {total_created} created, {total_updated} updated."
        ))
