from rest_framework import permissions


class CommunityPostPermission(permissions.BasePermission):
    """
    Authenticated users can read and create community posts.
    Authors can edit and soft-delete their own community posts.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
