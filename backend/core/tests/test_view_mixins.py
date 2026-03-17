from django.contrib.auth import get_user_model
from django.urls import path
from django.test import override_settings

from rest_framework import serializers, status
from rest_framework.test import APIRequestFactory
from rest_framework.viewsets import GenericViewSet

from articles.models import SourceArticle
from core.pagination import StandardPagination
from core.tests.testcases import BaseTestCase
from core.views.mixins import FormattedResponseMixin, MyListModelMixin


User = get_user_model()


class _SourceArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceArticle
        fields = ["id", "title"]


class _PaginatedArticleViewSet(FormattedResponseMixin, MyListModelMixin, GenericViewSet):
    serializer_class = _SourceArticleSerializer
    pagination_class = StandardPagination
    permission_classes = []

    def get_queryset(self):
        return SourceArticle.objects.order_by("created_at")


urlpatterns = [
    path(
        "test-articles/",
        _PaginatedArticleViewSet.as_view({"get": "list"}),
        name="test-article-list",
    ),
]


@override_settings(ROOT_URLCONF=__name__)
class MyListModelMixinTests(BaseTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username="viewer", password="secret123")
        for index in range(25):
            SourceArticle.objects.create(
                author=self.user,
                title=f"Article {index}",
                content={"index": index},
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
