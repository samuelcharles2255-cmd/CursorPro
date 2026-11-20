import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from apps.jobs.models import Job, Company, Skill


class Command(BaseCommand):
    help = "Seeds initial jobs and companies from the packaged fixture if the database is empty or requested."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force reload jobs fixture even if jobs already exist.",
        )

    def handle(self, *args, **options):
        force = options.get("force", False)
        job_count = Job.objects.count()

        if job_count > 0 and not force:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Database already has {job_count} jobs and {Company.objects.count()} companies. "
                    "Use --force to reload."
                )
            )
            return

        self.stdout.write("Loading jobs, companies, and skills from jobs_data.json...")
        call_command("loaddata", "jobs_data.json")
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully loaded jobs! Total jobs: {Job.objects.count()}, "
                f"Companies: {Company.objects.count()}, Skills: {Skill.objects.count()}."
            )
        )
