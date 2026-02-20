from rest_framework.permissions import BasePermission

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