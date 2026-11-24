from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CompanyViewSet,
    JobViewSet,
    SkillViewSet,
    JobApplicationViewSet,
    SavedJobViewSet,
)

router = DefaultRouter()
router.register("jobs", JobViewSet, basename="job")
router.register("companies", CompanyViewSet, basename="company")
router.register("skills", SkillViewSet, basename="skill")
router.register("job-applications", JobApplicationViewSet, basename="job-application")
router.register("saved-jobs", SavedJobViewSet, basename="saved-job")

urlpatterns = [
    path("", include(router.urls)),
]