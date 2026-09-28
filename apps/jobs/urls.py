from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CompanyViewSet, JobViewSet, SkillViewSet

router = DefaultRouter()
router.register("jobs", JobViewSet, basename="job")
router.register("companies", CompanyViewSet, basename="company")
router.register("skills", SkillViewSet, basename="skill")

urlpatterns = [
    path("", include(router.urls)),
]