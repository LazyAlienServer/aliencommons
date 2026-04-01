from rest_framework import permissions

from core.utils.permissions import is_moderator
from .models import ArticleEvent


def is_the_author(user, obj):
    return user.id == obj.author_id


class AuthorOnly(permissions.BasePermission):
    """
    Only the author can access his/her articles.
    Note that this only applies to detail actions.
    To guarantee author-only access, restrictions must also be added into get_queryset.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return is_the_author(request.user, obj)


class ModeratorOnly(permissions.BasePermission):
    """
    Only moderators can call certain endpoints.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and is_moderator(request.user)

    def has_object_permission(self, request, view, obj):
        return is_moderator(request.user)


class ArticleEventPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        obj: ArticleEvent
        return is_moderator(request.user) or is_the_author(request.user, obj.source_article)
