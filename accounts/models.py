from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.jobs.models import Company, Skill


class User(AbstractUser):
    """
    The single account model for the whole platform. Job seekers and
    employers are both Users, distinguished by `role`. Don't create a
    separate Employer model that duplicates login/password — that's how
    you end up building auth twice.
    """
    ROLE_JOB_SEEKER = "job_seeker"
    ROLE_EMPLOYER = "employer"
    ROLE_CHOICES = [
        (ROLE_JOB_SEEKER, "Job Seeker"),
        (ROLE_EMPLOYER, "Employer"),
    ]

    AUTH_EMAIL = "email"
    AUTH_GOOGLE = "google"
    AUTH_PROVIDER_CHOICES = [
        (AUTH_EMAIL, "Email/Password"),
        (AUTH_GOOGLE, "Google"),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_JOB_SEEKER)

    # groundwork for Google login — field exists now so no migration is
    # needed later, but nothing writes to it until GoogleLoginView is wired up
    auth_provider = models.CharField(max_length=20, choices=AUTH_PROVIDER_CHOICES, default=AUTH_EMAIL)
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # AbstractUser still wants a username internally

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email

    @property
    def is_employer(self):
        return self.role == self.ROLE_EMPLOYER


class Profile(models.Model):
    """
    Everything that ISN'T login/auth. Kept off the User model on purpose —
    auth stays lean and fast to query, profile can grow (resume, bio,
    avatar, skills) without touching the table Django checks on every request.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    resume_url = models.URLField(blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)

    # this is the piece that connects a user to jobs: match jobs.skills
    # against profile.skills to power "jobs matching you" later
    skills = models.ManyToManyField(Skill, through="ProfileSkill", related_name="profiles")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"

    def __str__(self):
        return f"Profile<{self.user.email}>"


class ProfileSkill(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        db_table = "user_skills"
        unique_together = ("profile", "skill")


class EmployerProfile(models.Model):
    """
    Only created for users with role=employer. Separate from Profile
    because an employer's relevant data (which company, verified or not)
    has nothing to do with a job seeker's bio/resume.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employer_profile")
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="employer_members"
    )
    job_title = models.CharField(max_length=255, blank=True)  # e.g. "HR Manager"
    # don't let anyone post jobs under a company until you've confirmed
    # they actually work there — otherwise anyone can post fake listings
    # under "Google" or "Safaricom"
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "employer_profiles"

    def __str__(self):
        return f"Employer<{self.user.email}>"