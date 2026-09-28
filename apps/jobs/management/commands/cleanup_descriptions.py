import logging
from django.core.management.base import BaseCommand
from apps.jobs.models import Job
from apps.jobs.cleaning import clean_job_description

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Cleans and normalizes all existing job descriptions in the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be cleaned without saving to the database.",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        jobs = list(Job.objects.all())
        total = len(jobs)
        cleaned_count = 0

        self.stdout.write(f"Found {total} jobs to check for description cleanup...")

        to_update = []
        for job in jobs:
            original = job.description or ""
            cleaned = clean_job_description(original, source=job.source)

            if cleaned != original:
                cleaned_count += 1
                job.description = cleaned
                to_update.append(job)

        self.stdout.write(f"Total jobs needing description cleanup: {cleaned_count}/{total}")

        if not dry_run and to_update:
            Job.objects.bulk_update(to_update, ["description"], batch_size=200)
            self.stdout.write(self.style.SUCCESS(f"Successfully cleaned and updated {cleaned_count} jobs!"))
        elif dry_run:
            self.stdout.write(self.style.NOTICE(f"[Dry Run] {cleaned_count} jobs would be updated."))
        else:
            self.stdout.write(self.style.SUCCESS("All job descriptions are already clean."))
