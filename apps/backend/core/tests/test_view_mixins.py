from django.contrib.auth import get_user_model
from django.urls import path
from django.test import override_settings

from rest_framework import serializers, status
from rest_framework.mixins import ListModelMixin
from rest_framework.test import APIRequestFactory
from rest_framework.viewsets import GenericViewSet

from articles.models import Article
from core.pagination import StandardPagination
from core.tests.factories import create_article
from core.tests.testcases import BaseTestCase
from drf_std_response import EnvelopeMixin


User = get_user_model()


class _ArticleSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="source.title", read_only=True)

    class Meta:
        model = Article
        fields = ["id", "title"]


class _PaginatedArticleViewSet(EnvelopeMixin, ListModelMixin, GenericViewSet):
    serializer_class = _ArticleSerializer
    pagination_class = StandardPagination
    permission_classes = []

    def get_queryset(self):
        return Article.objects.order_by("created_at")


class _NativeListArticleViewSet(EnvelopeMixin, ListModelMixin, GenericViewSet):
    serializer_class = _ArticleSerializer
    pagination_class = None
    permission_classes = []

    def get_queryset(self):
        return Article.objects.order_by("created_at")


urlpatterns = [
    path(
        "test-articles/",
        _PaginatedArticleViewSet.as_view({"get": "list"}),
        name="test-article-list",
    ),
]


@override_settings(ROOT_URLCONF=__name__)
class EnvelopeMixinTests(BaseTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username="viewer", password="secret123")
        for index in range(25):
            create_article(
                author=self.user,
                title=f"Article {index}",
                markdown=f"Article {index}",
            )

    def test_paginated_list_response_is_wrapped_with_standard_api_shape(self):
        request = self.factory.get("/test-articles/?page=2")
        request.user = self.user

        response = _PaginatedArticleViewSet.as_view({"get": "list"})(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["code"], "listed")
        self.assertEqual(response.data["message"], "listed")
        self.assertEqual(response.data["data"]["count"], 25)
        self.assertEqual(response.data["data"]["current_page"], 2)
        self.assertEqual(len(response.data["data"]["results"]), 5)

    def test_envelope_mixin_wraps_native_drf_list_response(self):
        request = self.factory.get("/test-articles/")
        request.user = self.user

        response = _NativeListArticleViewSet.as_view({"get": "list"})(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["code"], "listed")
        self.assertEqual(response.data["message"], "listed")
        self.assertEqual(len(response.data["data"]), 25)
