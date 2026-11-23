from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """
    Top-level category grouping marketplace listings (e.g., Electronics, Vehicles, Fashion, Real Estate).
    """
    name = models.CharField(_("name"), max_length=100, unique=True, db_index=True)
    slug = models.SlugField(_("slug"), max_length=120, unique=True, blank=True)
    description = models.TextField(_("description"), blank=True)
    icon = models.CharField(
        _("icon name"),
        max_length=50,
        default="tag",
        help_text=_("Frontend icon key (e.g. smartphone, car, laptop, home, shirt, shopping-bag)")
    )
    image = models.ImageField(_("category image"), upload_to="categories/covers/", null=True, blank=True)
    is_active = models.BooleanField(_("is active"), default=True, db_index=True)
    display_order = models.PositiveIntegerField(_("display order"), default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories_category"
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Subcategory(models.Model):
    """
    Secondary category refinement (e.g., Category: Electronics -> Subcategory: Mobile Phones, Laptops, Audio).
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories",
        verbose_name=_("parent category")
    )
    name = models.CharField(_("name"), max_length=100)
    slug = models.SlugField(_("slug"), max_length=120, blank=True)
    description = models.TextField(_("description"), blank=True)
    icon = models.CharField(_("icon name"), max_length=50, blank=True)
    is_active = models.BooleanField(_("is active"), default=True, db_index=True)
    display_order = models.PositiveIntegerField(_("display order"), default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories_subcategory"
        verbose_name = _("Subcategory")
        verbose_name_plural = _("Subcategories")
        unique_together = ("category", "slug")
        ordering = ["category", "display_order", "name"]

    def __str__(self):
        return f"{self.category.name} > {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
