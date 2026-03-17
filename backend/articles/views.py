from django_filters import rest_framework as filters
from django.db.models import OuterRef, Subquery
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from core.utils.permissions import is_moderator
from core.views.viewsets import MyModelViewSet, MyReadOnlyModelViewSet
from .filters import SourceArticleFilter
from .permissions import (
    AuthorOnly,
    ModeratorOnly,
    ArticleEventPermission,
)
from .models import SourceArticle, PublishedArticle, ArticleSnapshot, ArticleEvent
from .serializers import (
    SourceArticleReadSerializer,
    SourceArticleWriteSerializer,
    ImageUploadSerializer,
    PublishedArticleSerializer,
    ArticleSnapshotSerializer,
    ArticleEventSerializer,
    ArticleActionInputSerializer,
    ArticleActionOutputSerializer,
)
from .services.articles import (
    submit, withdraw, approve, reject, unpublish, soft_delete
)


class SourceArticleViewSet(MyModelViewSet):
    queryset = SourceArticle.objects.select_related("author")
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SourceArticleFilter

    permission_class_mapping = {
        'create': [IsAuthenticated],
        'list': [AuthorOnly],
        'retrieve': [AuthorOnly],
        'update': [AuthorOnly],
        'partial_update': [AuthorOnly],
        'destroy': [AuthorOnly],
        'upload_images': [AuthorOnly],
        'submit': [AuthorOnly],
        'withdraw': [AuthorOnly],
        'approve': [ModeratorOnly],
        'reject': [ModeratorOnly],
        'unpublish': [ModeratorOnly],
        'trash': [AuthorOnly],
    }

    def get_serializer_class(self):
        # Author - Write Serializer | Moderators - Read Serializer
        self.action: str
        if self.action in ('create', 'update', 'partial_update'):
            return SourceArticleWriteSerializer
        return SourceArticleReadSerializer

    def get_permissions(self):
        self.action: str
        self.permission_classes = self.permission_class_mapping[self.action]

        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        # Only authors can see his/her articles
        user = self.request.user
        queryset = super().get_queryset()

        if not user or user.is_anonymous:
            return queryset.none()

        queryset = queryset.filter(author=user)
        last_snapshot_id = (
            ArticleSnapshot.objects
            .filter(source_article_id=OuterRef("pk"))
            .order_by("-created_at")
            .values("id")[:1]
        )
        published_version_id = PublishedArticle.objects.filter(source_article_id=OuterRef("pk")).values("id")

        return queryset.annotate(
            last_snapshot_id=Subquery(last_snapshot_id),
            published_version_id=Subquery(published_version_id),
        )

    def create(self, request, *args, **kwargs):
        input_serializer = SourceArticleWriteSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        input_serializer.is_valid(raise_exception=True)

        source_article = input_serializer.save(author=self.request.user)

        output_serializer = SourceArticleReadSerializer(
            instance=source_article,
            context=self.get_serializer_context(),
        )

        return self.format_success_response(
            message="created",
            code='created',
            data=output_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['post'], url_path='images')
    def upload_images(self, request):
        serializer = ImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()

        return self.format_success_response(
            message="uploaded",
            code='uploaded',
            data=result,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        input_serializer = ArticleActionInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        result = submit(
            source_article_id=pk,
            actor=request.user,
            annotation=input_serializer.validated_data.get("annotation", None)
        )

        output_serializer = ArticleActionOutputSerializer(instance=result)

        return self.format_success_response(
            message="submitted",
            code='submitted',
            data=output_serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        input_serializer = ArticleActionInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        result = withdraw(
            source_article_id=pk,
            actor=request.user,
            annotation=input_serializer.validated_data.get("annotation", None)
        )

        output_serializer = ArticleActionOutputSerializer(instance=result)

        return self.format_success_response(
            message="withdrawn",
            code='withdrawn',
            data=output_serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        input_serializer = ArticleActionInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        result = approve(
            source_article_id=pk,
            actor=request.user,
            annotation=input_serializer.validated_data.get("annotation", None)
        )

        output_serializer = ArticleActionOutputSerializer(instance=result)

        return self.format_success_response(
            message="approved",
            code='approved',
            data=output_serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        input_serializer = ArticleActionInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        result = reject(
            source_article_id=pk,
            actor=request.user,
            annotation=input_serializer.validated_data.get("annotation", None)
        )

        output_serializer = ArticleActionOutputSerializer(instance=result)

        return self.format_success_response(
            message="rejected",
            code='rejected',
            data=output_serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        input_serializer = ArticleActionInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        result = unpublish(
            source_article_id=pk,
            actor=request.user,
            annotation=input_serializer.validated_data.get("annotation", None)
        )

        output_serializer = ArticleActionOutputSerializer(instance=result)

        return self.format_success_response(
            message="unpublished",
            code='unpublished',
            data=output_serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'])
    def trash(self, request, pk=None):
        input_serializer = ArticleActionInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        result = soft_delete(
            source_article_id=pk,
            actor=request.user,
            annotation=input_serializer.validated_data.get("annotation", None)
        )

        output_serializer = ArticleActionOutputSerializer(instance=result)

        return self.format_success_response(
            message="deleted",
            code='deleted',
            data=output_serializer.data,
            status_code=status.HTTP_200_OK,
        )


class PublishedArticleViewSet(MyReadOnlyModelViewSet):
    queryset = PublishedArticle.objects.all()
    serializer_class = PublishedArticleSerializer
    permission_classes = [IsAuthenticated]


class ArticleSnapshotViewSet(MyReadOnlyModelViewSet):
    queryset = ArticleSnapshot.objects.all()
    serializer_class = ArticleSnapshotSerializer
    permission_classes = [ModeratorOnly]

    @action(detail=False, methods=['get'])
    def pending_ones(self, request):
        """
        Return not moderated article snapshots
        """
        queryset = ArticleSnapshot.objects.filter(moderation_status=ArticleSnapshot.SnapshotStatus.PENDING)
        serializer = self.get_serializer(queryset, many=True)

        return self.format_success_response(
            message="pending articles listed",
            code='listed',
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class ArticleEventReadViewset(MyReadOnlyModelViewSet):
    queryset = ArticleEvent.objects.all()
    permission_classes = (ArticleEventPermission,)
    serializer_class = ArticleEventSerializer

    def get_queryset(self):
        user = self.request.user
        if is_moderator(user):
            return ArticleEvent.objects.all()
        return ArticleEvent.objects.filter(source_article__author=user)
