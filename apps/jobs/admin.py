from django.contrib import admin

from .models import Job, Company,JobSource


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "ats_type",
        "ats_identifier",
        "active",
    )

    list_filter = (
        "ats_type",
        "active",
    )
@admin.register(JobSource)
class JobSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "is_active", "needs_js", "last_status", "last_run_at")
    list_filter = ("is_active", "last_status")
    actions = ["run_now"]

    @admin.action(description="Run agent now for selected sources")
    def run_now(self, request, queryset):
        from .agents.runner import run_source
        for source in queryset:
            run_source(source)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "company",
        "organization",
        "source",
        "job_source",
        "location",
        "created_at",
        "deadline",
        "is_active",
    )

    list_filter = (
        "source",
        "job_source",
        "is_active",
    )

    search_fields = (
        "title",
        "company__name",
        "location",
        "organization",
    )