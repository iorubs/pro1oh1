from rest_framework import permissions


class IsAuthorOfProject(permissions.BasePermission):
    def has_object_permission(self, request, view, project):
        if request.user:
            return project.author == request.user
        return False

class IsAuthorOfFile(permissions.BasePermission):
    def has_object_permission(self, request, view, file):
        if request.user:
            return file.project.author == request.user
        return False
