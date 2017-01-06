from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, project):
        if request.user:
            return request.user.is_admin
        return False
