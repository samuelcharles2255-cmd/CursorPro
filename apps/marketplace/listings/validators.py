import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

MAX_IMAGE_SIZE_MB = 5
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]


def validate_listing_image(file):
    """
    Validates uploaded listing image size and file extension.
    Ensures files are valid images under MAX_IMAGE_SIZE_MB.
    """
    if file.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(
            _(f"Image size exceeds {MAX_IMAGE_SIZE_MB}MB limit. Current size is {file.size / (1024 * 1024):.2f}MB."),
            code="image_too_large"
        )

    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            _(f"Unsupported image format '{ext}'. Allowed formats are: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}."),
            code="unsupported_image_format"
        )
