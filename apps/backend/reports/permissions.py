from rest_framework import permissions

from core.utils.permissions import is_moderator


class ReportPermission(permissions.BasePermission):
    """
    Users can create and read their own reports.
    Moderators can read and update all reports.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if view.action in ("update", "partial_update"):
            return is_moderator(request.user)
        return True

    def has_object_permission(self, request, view, obj):
        if is_moderator(request.user):
            return True
        if request.method in permissions.SAFE_METHODS:
            return obj.reporter_id == request.user.id
        return False

