from rest_framework import serializers

from .models import Company, Job, Skill


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
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = "__all__"