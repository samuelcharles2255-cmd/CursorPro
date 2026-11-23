import django_filters
from django.db.models import Q
from .models import Listing


class ListingFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search", label="Search title and description")
    category = django_filters.CharFilter(method="filter_category", label="Category ID or Slug")
    subcategory = django_filters.CharFilter(method="filter_subcategory", label="Subcategory ID or Slug")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    region = django_filters.CharFilter(field_name="region", lookup_expr="iexact")
    district = django_filters.CharFilter(field_name="district", lookup_expr="iexact")
    condition = django_filters.CharFilter(field_name="condition", lookup_expr="iexact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")

    class Meta:
        model = Listing
        fields = [
            "search", "category", "subcategory", "min_price",
            "max_price", "region", "district", "condition", "status"
        ]

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        val = value.strip()
        return queryset.filter(
            Q(title__icontains=val) | Q(description__icontains=val)
        )

    def filter_category(self, queryset, name, value):
        if not value:
            return queryset
        if value.isdigit():
            return queryset.filter(category_id=int(value))
        return queryset.filter(category__slug__iexact=value)

    def filter_subcategory(self, queryset, name, value):
        if not value:
            return queryset
        if value.isdigit():
            return queryset.filter(subcategory_id=int(value))
        return queryset.filter(subcategory__slug__iexact=value)
