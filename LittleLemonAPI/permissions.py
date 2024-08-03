from rest_framework.permissions import BasePermission

class ManagerRole(BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name="Manager").exists():
            return True
        else:
            return False