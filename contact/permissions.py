from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """
    Allows access only to Django superusers.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
