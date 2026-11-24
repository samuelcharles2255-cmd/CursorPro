from rest_framework import serializers

from .models import Company, Job, Skill, JobApplication, SavedJob


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "website", "career_page", "country", "logo"]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]


class JobSerializer(serializers.ModelSerializer):
    """Lightweight version — used for list/feed views."""
    company_name = serializers.CharField(source="company.name", read_only=True)
    company_logo = serializers.CharField(source="company.logo", read_only=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company",
            "company_name",
            "company_logo",
            "location",
            "country",
            "employment_type",
            "salary_min",
            "salary_max",
            "salary_currency",
            "posted_at",
            "expires_at",
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    """Full version — used when the user taps into a single job."""
    company = CompanySerializer(read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = "__all__"


class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    company_name = serializers.CharField(source="job.company.name", read_only=True, default="")
    company_logo = serializers.CharField(source="job.company.logo", read_only=True, default="")
    location = serializers.CharField(source="job.location", read_only=True, default="")

    class Meta:
        model = JobApplication
        fields = [
            "id", "job", "job_title", "company_name", "company_logo",
            "location", "full_name", "email", "phone", "cover_letter",
            "resume_url", "status", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at"]


class CreateJobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ["job", "full_name", "email", "phone", "cover_letter", "resume_url"]

    def create(self, validated_data):
        user = self.context["request"].user
        return JobApplication.objects.create(user=user, **validated_data)


class SavedJobSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source="job", read_only=True)

    class Meta:
        model = SavedJob
        fields = ["id", "job", "job_details", "created_at"]
        read_only_fields = ["id", "created_at"]
