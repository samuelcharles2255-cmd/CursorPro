from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Company, Job, Skill
from .serializers import (
    CompanySerializer,
    JobDetailSerializer,
    JobSerializer,
    SkillSerializer,
)


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only: users browse and tap through to apply on the company's
    site — they don't create/edit jobs through this API.

    GET /jobs/                     -> list (filterable, searchable)
    GET /jobs/<id>/                -> full detail, used for the tap-in view
    GET /jobs/?search=python       -> free-text search
    GET /jobs/?employment_type=full_time&country=Tanzania
    GET /jobs/?ordering=-posted_at
    GET /jobs/?include_expired=true -> also show expired listings
    """
    queryset = Job.objects.select_related("company").prefetch_related("skills")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["employment_type", "country", "source", "company"]
    search_fields = ["title", "description", "location"]
    ordering_fields = ["posted_at", "salary_min", "salary_max"]
    ordering = ["-posted_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return JobDetailSerializer
        return JobSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # hide expired jobs by default — nobody should tap into a dead listing
        if self.request.query_params.get("include_expired") != "true":
            qs = qs.filter(Q(expires_at__isnull=True) | Q(expires_at__gte=timezone.now()))
        return qs


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]