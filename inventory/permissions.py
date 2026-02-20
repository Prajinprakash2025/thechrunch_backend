from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_superuser)

class IsOwner(BasePermission):
    def has_permission(self, request, view):
        # Allow if they have the owner role OR if they are a superuser
        return bool(
            request.user.is_authenticated and
            (request.user.role == "owner" or request.user.is_superuser)
        )
    
class IsOwnerOrEmployee(BasePermission):
    def has_permission(self, request, view):
        # Allow if they are an owner, an employee, OR a superuser
        return bool(
            request.user.is_authenticated and
            (request.user.role in ["owner", "employee"] or request.user.is_superuser)
        )