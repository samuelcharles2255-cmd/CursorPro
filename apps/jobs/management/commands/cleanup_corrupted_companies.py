import re
import logging
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.jobs.models import Company, Job
from apps.jobs.cleaning import clean_job_description

logger = logging.getLogger(__name__)

STOP_MARKERS = [
    "Check all: JOBS IN TANZANIA",
    "How to Apply for this JobNo separate application link",
    "How to Apply for this Job",
    "More job opportunitiesRelated Jobs",
    "Jobs & CareersMabumbe.com",
    "Share Facebook WhatsApp LinkedIn",
]

START_MARKERS = [
    "Job DescriptionAdvertisement",
    "Job Description",
]


def extract_description_from_blob(raw_text: str) -> str:
    """Extracts the actual job description from a scraped page blob."""
    if not raw_text:
        return ""
    start_pos = 0
    for sm in START_MARKERS:
        idx = raw_text.find(sm)
        if idx != -1:
            start_pos = idx + len(sm)
            break
    end_pos = len(raw_text)
    for em in STOP_MARKERS:
        idx = raw_text.find(em, start_pos)
        if idx != -1 and idx < end_pos:
            end_pos = idx
    extracted = raw_text[start_pos:end_pos].strip()
    return clean_job_description(extracted, source="api")


class Command(BaseCommand):
    help = "Repairs companies that were corrupted with scraped webpage content and restores job descriptions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the cleanup without committing database changes.",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        if dry_run:
            self.stdout.write(self.style.NOTICE("DRY RUN - No changes will be saved to the database."))

        # Explicit target mappings for the known corrupted entries
        RENAME_MAP = {
            55: "Kafika House",
            56: "Médecins Sans Frontières (MSF)",
            62: "Miracle Experience",
        }

        MIGRATE_MAP = {
            45: 44,  # Equity Bank
            46: 44,  # Equity Bank
            58: 59,  # SWISSAID Tanzania
            61: 60,  # Enza Zaden Africa Limited
            64: 62,  # Miracle Experience
        }

        corrupted_companies = list(
            Company.objects.filter(name__icontains="Skip to content")
        )
        self.stdout.write(f"Found {len(corrupted_companies)} corrupted company records.")

        if not corrupted_companies:
            self.stdout.write(self.style.SUCCESS("No corrupted companies found."))
            return

        with transaction.atomic():
            # Step 1: Process renames first so target companies exist for migrations
            for comp_id, new_name in RENAME_MAP.items():
                comp = Company.objects.filter(id=comp_id).first()
                if not comp:
                    continue
                self.stdout.write(f"\n[Step 1] Renaming Company ID {comp.id} -> '{new_name}'")
                raw_blob = comp.name
                cleaned_desc = extract_description_from_blob(raw_blob)

                for job in comp.jobs.all():
                    self.stdout.write(f"  Updating Job {job.id} ('{job.title[:50]}')...")
                    if not dry_run:
                        if cleaned_desc and not job.description:
                            job.description = cleaned_desc
                        job.organization = new_name
                        job.save(update_fields=["organization", "description"])

                if not dry_run:
                    comp.name = new_name
                    comp.country = comp.country or "Tanzania"
                    comp.active = True
                    comp.save(update_fields=["name", "country", "active"])
                self.stdout.write(self.style.SUCCESS(f"  Company {comp_id} renamed to '{new_name}'"))

            # Step 2: Migrate jobs from obsolete companies to target companies
            for comp_id, target_comp_id in MIGRATE_MAP.items():
                comp = Company.objects.filter(id=comp_id).first()
                if not comp:
                    continue
                target_comp = Company.objects.filter(id=target_comp_id).first()
                if not target_comp:
                    self.stdout.write(self.style.ERROR(f"Target company {target_comp_id} not found for {comp_id}!"))
                    continue

                self.stdout.write(f"\n[Step 2] Migrating Company ID {comp.id} -> Target '{target_comp.name}' (ID {target_comp.id})")
                raw_blob = comp.name
                cleaned_desc = extract_description_from_blob(raw_blob)

                for job in comp.jobs.all():
                    self.stdout.write(f"  Reassigning Job {job.id} ('{job.title[:50]}') to Company {target_comp.id}")
                    if not dry_run:
                        job.company = target_comp
                        job.organization = target_comp.name
                        if cleaned_desc and not job.description:
                            job.description = cleaned_desc
                        job.save(update_fields=["company", "organization", "description"])

                if not dry_run:
                    comp.delete()
                    self.stdout.write(self.style.SUCCESS(f"  Deleted obsolete company ID {comp_id}"))

            # Step 3: Check for any remaining corrupted companies (> 100 chars or containing "Skip to content")
            remaining = Company.objects.filter(name__icontains="Skip to content")
            if not dry_run and remaining.exists():
                for rem in remaining:
                    self.stdout.write(self.style.WARNING(f"Cleaning remaining corrupted company {rem.id}"))
                    clean_name = re.sub(r"Skip to content.*?(at\s+)?", "", rem.name, flags=re.I)[:80].strip() or f"Company {rem.id}"
                    rem.name = clean_name
                    rem.save(update_fields=["name"])

            if dry_run:
                self.stdout.write(self.style.NOTICE("\nDry run completed. Rolling back transaction."))
                transaction.set_rollback(True)
            else:
                self.stdout.write(self.style.SUCCESS("\nAll corrupted companies repaired and cleaned successfully!"))
