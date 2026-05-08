from rest_framework import permissions


class BookmarkOwnerOnly(permissions.BasePermission):
    """
    Bookmarks and folders are private to their owning user.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id
