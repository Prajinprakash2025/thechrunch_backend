from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied  

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_superuser)

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        # Allow if they have the 'admin' role OR if they are a superuser
        return bool(
            request.user.is_authenticated and
            (request.user.role == "admin" or request.user.is_superuser)
        )

class IsAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        # Allow if they are an admin, staff, OR a superuser
        return bool(
            request.user.is_authenticated and
            (request.user.role in ["admin", "staff"] or request.user.is_superuser)
        )

# ==========================================
# 🚀 NEW PERMISSION: Blocked Users Check
# ==========================================
class IsNotBlocked(BasePermission):
    """
    Global permission check for blocked users.
    If a user is blocked, this will throw a 403 Forbidden error on any API request.
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            # Check if the user is blocked
            if getattr(request.user, 'is_blocked', False):
                # Throw immediate 403 error
                raise PermissionDenied(detail="Your account has been blocked by the admin. You are logged out.")
        return True