import re
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Company(models.Model):

    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(blank=True, null=True)
    career_page = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True)
    logo = models.URLField(blank=True, null=True)  # storing a link, not uploading files

    ATS_CHOICES = [
        ("greenhouse", "Greenhouse"),
        ("lever", "Lever"),
        ("workday", "Workday"),
    ]
    ats_type = models.CharField(
        max_length=50,
        choices=ATS_CHOICES,
        blank=True,
        default=""
    )

    ats_identifier = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    career_url = models.URLField(
        blank=True
    )

    active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "companies"
        ordering = ["name"]

    def clean(self):
        super().clean()
        if self.name:
            self.name = re.sub(r"\s+", " ", self.name).strip()
            if len(self.name) > 255:
                self.name = self.name[:255].strip()

    def save(self, *args, **kwargs):
        if self.name:
            self.name = re.sub(r"\s+", " ", self.name).strip()
            if "skip to content" in self.name.lower():
                m = re.search(r"\bat\s+([^–\-\(\d\n]+)", self.name, re.I)
                self.name = m.group(1).strip() if m else "Tanzania Employer"
            if len(self.name) > 255:
                self.name = self.name[:255].strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "skills"
        ordering = ["name"]

    def __str__(self):
        return self.name


class JobSource(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=1000)
    needs_js = models.BooleanField(default=False)  # True for JS-heavy sites
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(max_length=20, blank=True)
    last_error = models.TextField(blank=True)
    last_content_hash = models.CharField(max_length=64, blank=True)

    check_every_days = models.PositiveSmallIntegerField(default=1)
    fail_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "job_sources"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Job(models.Model):
    # where the job record came from — matches your 3 sources
    SOURCE_API = "api"
    SOURCE_CAREER_PAGE = "career_page"
    SOURCE_DIRECT = "direct"
    SOURCE_CHOICES = [
        (SOURCE_API, "Job Platform API"),
        (SOURCE_CAREER_PAGE, "Company Career Page"),
        (SOURCE_DIRECT, "Direct Company Website"),
    ]

    EMPLOYMENT_CHOICES = [
        ("full_time", "Full-time"),
        ("part_time", "Part-time"),
        ("contract", "Contract"),
        ("internship", "Internship"),
        ("freelance", "Freelance"),
    ]

    title = models.CharField(max_length=255, db_index=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs", null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, db_index=True)
    country = models.CharField(max_length=100, blank=True, db_index=True)
    description = models.TextField()
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES, blank=True)

    # split out of your single "salary" field so it's actually filterable/sortable
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=10, blank=True)

    experience_required = models.CharField(max_length=255, blank=True)
    education_required = models.CharField(max_length=255, blank=True)

    application_url = models.URLField(max_length=1000)  # where the "apply" tap sends the user
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_DIRECT)
    source_job_id = models.CharField(max_length=255, blank=True, null=True)

    skills = models.ManyToManyField(Skill, through="JobSkill", related_name="jobs")

    posted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    ## FOR AI SCRAPING FROM OTHER PLATFORMS
    job_source = models.ForeignKey(
        JobSource,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="jobs",
    )
    organization = models.CharField(max_length=200, blank=True)
    deadline = models.DateField(null=True, blank=True)
    fingerprint = models.CharField(max_length=64, unique=True, null=True, blank=True)
    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "jobs"
        ordering = ["-posted_at"]
        constraints = [
            # stops the same job from being re-inserted every time a source re-syncs
            models.UniqueConstraint(
                fields=["source", "source_job_id"],
                name="unique_source_job",
                condition=Q(source_job_id__isnull=False),
            )
        ]
        indexes = [
            models.Index(fields=["title", "location"]),
        ]

    def __str__(self):
        comp = self.company.name if self.company else (self.organization or "Unknown")
        return f"{self.title} @ {comp}"

    @property
    def is_expired(self):
        return bool(self.expires_at and self.expires_at < timezone.now())

    @property
    def apply_url(self):
        return self.application_url


class JobSkill(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        db_table = "job_skills"
        unique_together = ("job", "skill")

# User, Profile and UserSkill now live in the `accounts` app —
# auth is infrastructure, not a jobs-feature. See accounts/models.py.
