from django.contrib import admin

from .models import Job, Company


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


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "company",
        "source",
        "location",
        "created_at",
    )

    list_filter = (
        "source",
    )

    search_fields = (
        "title",
        "company",
        "location",
    )