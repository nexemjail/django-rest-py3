from rest_framework.permissions import BasePermission


class IsMediaAuthoredBy(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.event.user == request.user


class IsAuthoredBy(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
