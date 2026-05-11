from django.contrib.auth.models import AnonymousUser

from rest_framework.test import APIRequestFactory

from core.tests.factories import create_user
from core.tests.testcases import BaseTestCase
from posts.models import CommunityPost
from posts.permissions import CommunityPostPermission


class CommunityPostPermissionTests(BaseTestCase):
    def setUp(self):
        self.permission = CommunityPostPermission()
        self.factory = APIRequestFactory()
        self.author = create_user(username="post-author")
        self.other_user = create_user(username="other-user")
        self.post = CommunityPost.objects.create(author=self.author, body="Hello community")

    def request(self, method, user):
        request = getattr(self.factory, method.lower())("/posts/")
        request.user = user
        return request

    def test_anonymous_users_do_not_have_general_permission(self):
        request = self.request("get", AnonymousUser())

        self.assertFalse(self.permission.has_permission(request, None))

    def test_authenticated_users_have_general_permission(self):
        request = self.request("get", self.author)

        self.assertTrue(self.permission.has_permission(request, None))

    def test_safe_object_methods_are_allowed_for_authenticated_users(self):
        request = self.request("get", self.other_user)

        self.assertTrue(self.permission.has_object_permission(request, None, self.post))

    def test_author_can_modify_own_post(self):
        request = self.request("patch", self.author)

        self.assertTrue(self.permission.has_object_permission(request, None, self.post))

    def test_other_user_cannot_modify_post(self):
        request = self.request("patch", self.other_user)

        self.assertFalse(self.permission.has_object_permission(request, None, self.post))
