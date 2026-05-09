from rest_framework import permissions


class CommentPermission(permissions.BasePermission):
    """
    Authenticated users can read and create comments.
    Authors can edit and soft-delete their own comments.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author_id == request.user.id

