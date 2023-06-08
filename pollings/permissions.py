import rest_framework.permissions
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class UserViewPermission(BasePermission):
    def has_permission(self, request: Request, view):
        if request.method in ("POST", "HEAD"):
            return True
        if request.user is False:
            return False
        if (view.action == 'list' or request.method == "DELETE") \
                and request.user.is_staff is False:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.method == "HEAD" or request.user.is_staff or obj.id == request.user.id:
            return True
        return False


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in rest_framework.permissions.SAFE_METHODS:
            return True
        if request.user.is_staff or obj.author_id == request.user.id:
            return True
        return False
