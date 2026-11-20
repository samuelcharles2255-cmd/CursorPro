import re
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.jobs.models import Job, Skill, JobSkill

SKILL_DEFINITIONS = {
    "Python": r"\bpython\b",
    "Django": r"\bdjango\b",
    "JavaScript": r"\b(?:javascript|js)\b",
    "TypeScript": r"\btypescript\b",
    "React": r"\breact(?:\.js)?\b",
    "Node.js": r"\bnode(?:\.js)?\b",
    "Java": r"\bjava\b(?!script)",
    "Go": r"\b(?:golang|go\s+language)\b",
    "C#": r"\bc#|\bc-sharp\b",
    "C++": r"\bc\+\+\b",
    "PHP": r"\bphp\b",
    "Ruby": r"\bruby\b",
    "SQL": r"\bsql\b",
    "PostgreSQL": r"\b(?:postgresql|postgres)\b",
    "MySQL": r"\bmysql\b",
    "MongoDB": r"\bmongodb\b",
    "Redis": r"\bredis\b",
    "AWS": r"\baws\b|\bamazon\s+web\s+services\b",
    "Azure": r"\bazure\b",
    "GCP": r"\bgcp\b|\bgoogle\s+cloud\b",
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\b(?:kubernetes|k8s)\b",
    "Linux": r"\blinux\b",
    "Git": r"\bgit\b",
    "REST API": r"\brest(?:ful)?\s+api[s]?\b",
    "GraphQL": r"\bgraphql\b",
    "HTML/CSS": r"\bhtml\b|\bcss\b",
    "Tailwind CSS": r"\btailwind\b",
    "Sales": r"\bsales\b",
    "Marketing": r"\bmarketing\b",
    "Digital Marketing": r"\bdigital\s+marketing\b",
    "SEO": r"\bseo\b",
    "Product Management": r"\bproduct\s+management\b",
    "Project Management": r"\bproject\s+management\b",
    "Accounting": r"\baccounting\b",
    "Finance": r"\bfinance\b|\bfinancial\b",
    "Customer Service": r"\bcustomer\s+(?:service|support)\b",
    "UI/UX Design": r"\b(?:ui/ux|ux/ui|product\s+design)\b",
    "Figma": r"\bfigma\b",
    "Data Analysis": r"\bdata\s+analysis\b|\bdata\s+analytics\b",
    "Machine Learning": r"\bmachine\s+learning\b|\bml\b",
    "Excel": r"\bexcel\b",
    "Agile": r"\bagile\b|\bscrum\b",
}


class Command(BaseCommand):
    help = "Extracts skills from job descriptions and associates them with jobs."

    def handle(self, *args, **options):
        self.stdout.write("Populating skills from job descriptions...")
        
        # 1. Create all Skill objects
        skill_objs = {}
        for name in SKILL_DEFINITIONS:
            skill, _ = Skill.objects.get_or_create(name=name)
            skill_objs[name] = skill

        # Pre-compile patterns
        compiled_patterns = {
            name: re.compile(pat, re.IGNORECASE)
            for name, pat in SKILL_DEFINITIONS.items()
        }

        # 2. Extract skills per job in memory
        job_skills_to_create = []
        jobs = Job.objects.only("id", "title", "description").all()
        for job in jobs:
            text = f"{job.title} {job.description}"
            for name, pattern in compiled_patterns.items():
                if pattern.search(text):
                    job_skills_to_create.append(
                        JobSkill(job_id=job.id, skill_id=skill_objs[name].id)
                    )

        # 3. Fast bulk_create with ignore_conflicts
        with transaction.atomic():
            JobSkill.objects.bulk_create(job_skills_to_create, ignore_conflicts=True)

        total_skills = Skill.objects.count()
        total_links = JobSkill.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully extracted skills! Total skills tracked: {total_skills}, Total job-skill links: {total_links}"
            )
        )
