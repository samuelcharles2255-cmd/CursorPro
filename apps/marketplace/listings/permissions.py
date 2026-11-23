from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission allowing read-only access to any request,
    while restricting write/edit/delete operations strictly to the listing owner/seller.
    """
    def has_object_permission(self, request, view, obj):
        # Read-only permissions are allowed for safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the listing
        return getattr(obj, "seller", None) == request.user or (
            hasattr(request.user, "is_staff") and request.user.is_staff
        )
