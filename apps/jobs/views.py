from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Company, Job, Skill, JobApplication, SavedJob
from .serializers import (
    CompanySerializer,
    JobDetailSerializer,
    JobSerializer,
    SkillSerializer,
    JobApplicationSerializer,
    CreateJobApplicationSerializer,
    SavedJobSerializer,
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
    ordering_fields = ["posted_at", "created_at", "salary_min", "salary_max"]
    # Scraped jobs (NMB, Equity, etc.) have NULL posted_at — fall back to created_at
    # so freshly-scraped jobs appear near the top rather than sinking to the bottom.
    ordering = ["-posted_at", "-created_at"]

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

    @action(detail=False, methods=["get"])
    def stats(self, request):
        now = timezone.now()
        total_jobs = Job.objects.count()
        active_jobs = Job.objects.filter(Q(expires_at__isnull=True) | Q(expires_at__gte=now)).count()
        total_companies = Company.objects.count()
        return Response({
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_companies": total_companies,
            "verified_count": active_jobs,
        })



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


class JobApplicationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user).select_related("job", "job__company")

    def get_serializer_class(self):
        if self.action in ["create"]:
            return CreateJobApplicationSerializer
        return JobApplicationSerializer

    def create(self, request, *args, **kwargs):
        job_id = request.data.get("job")
        if not job_id:
            return Response({"error": "job ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        job = get_object_or_404(Job, pk=job_id)
        existing = JobApplication.objects.filter(user=request.user, job=job).first()
        if existing:
            return Response(
                {"detail": "You have already submitted an application for this position.", "id": existing.id},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        return Response(JobApplicationSerializer(application).data, status=status.HTTP_201_CREATED)


class SavedJobViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SavedJobSerializer

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).select_related("job", "job__company")

    @action(detail=False, methods=["post"])
    def toggle(self, request):
        job_id = request.data.get("job_id") or request.data.get("job")
        if not job_id:
            return Response({"error": "job_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        job = get_object_or_404(Job, pk=job_id)
        saved = SavedJob.objects.filter(user=request.user, job=job).first()
        if saved:
            saved.delete()
            return Response({"saved": False, "message": "Job removed from saved roles."})

        saved_item = SavedJob.objects.create(user=request.user, job=job)
        return Response(
            {"saved": True, "message": "Job bookmarked to saved roles.", "id": saved_item.id},
            status=status.HTTP_201_CREATED
        )
