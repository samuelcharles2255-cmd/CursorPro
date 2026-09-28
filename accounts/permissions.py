from rest_framework.permissions import BasePermission


class IsEmployer(BasePermission):
    """Use on any view where only employer accounts should act — e.g. posting a job later."""
    message = "Only employer accounts can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_employer)


class IsProfileOwner(BasePermission):
    """Object-level: a user can only edit their own profile, never someone else's."""
    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id