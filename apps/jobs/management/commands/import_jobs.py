import logging

from django.core.management.base import BaseCommand

from apps.jobs.models import Company
from apps.jobs.services import sync_company_ats_jobs

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
    help = "Import jobs from company ATS platforms (Greenhouse, Lever, Workday) using service files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--ats",
            type=str,
            choices=["greenhouse", "lever", "workday"],
            help="Filter import to only this ATS type.",
        )
        parser.add_argument(
            "--company",
            type=str,
            help="Filter import to a specific company by name or ats_identifier.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum number of jobs to import per company.",
        )
        parser.add_argument(
            "--seed",
            action="store_true",
            help="Seed sample verified companies for Greenhouse, Lever, and Workday before running.",
        )

    def handle(self, *args, **options):
        ats_filter = options.get("ats")
        company_filter = options.get("company")
        limit = options.get("limit")
        seed = options.get("seed")

        if seed:
            self.stdout.write(self.style.NOTICE("Seeding default verified companies for Greenhouse, Lever, and Workday..."))
            ensure_seed_companies()

        companies = Company.objects.filter(active=True).exclude(ats_type="")

        # If no companies with ats_type exist, auto-seed sample companies so user isn't stuck
        if not companies.exists() and not company_filter:
            self.stdout.write(
                self.style.NOTICE("No active ATS companies found. Auto-seeding verified sample companies (Stripe, Figma, Lever Demo, Salesforce)...")
            )
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
            self.stdout.write(
                self.style.WARNING("No matching active companies found with an ATS configured.")
            )
            return

        total_created = 0
        total_updated = 0

        for company in companies:
            self.stdout.write(f"Importing from {company.name} ({company.ats_type})...")

            try:
                created, updated = sync_company_ats_jobs(company, limit=limit)
                total_created += created
                total_updated += updated
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  -> {company.name}: {created} created, {updated} updated"
                    )
                )
            except Exception as error:
                logger.exception("import_jobs failed for %s", company.name)
                self.stdout.write(
                    self.style.ERROR(f"  -> Failed for {company.name}: {error}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! Total: {total_created} created, {total_updated} updated."
            )
        )
