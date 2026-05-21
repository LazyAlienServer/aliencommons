from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from articles.models import PublishedArticle
from core.views.viewsets import MyModelViewSet
from posts.models import CommunityPost
from .models import Reaction
from .serializers import ReactionReadSerializer, ReactionWriteSerializer
from .services import (
    clear_community_post_reaction,
    clear_published_article_reaction,
    set_community_post_reaction,
    set_published_article_reaction,
    update_reaction_type,
)


class ReactionViewSet(MyModelViewSet):
    queryset = Reaction.objects.select_related(
        "user",
        "target",
        "target__published_article",
        "target__community_post",
    )
    permission_classes = [IsAuthenticated]
    default_serializer_class = ReactionReadSerializer
    serializer_class_mapping = {
        "create": ReactionWriteSerializer,
        "update": ReactionWriteSerializer,
        "partial_update": ReactionWriteSerializer,
    }

    def get_serializer_class(self):
        self.action: str
        return self.serializer_class_mapping.get(self.action, self.default_serializer_class)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        input_serializer = ReactionWriteSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        input_serializer.is_valid(raise_exception=True)
        if "published_article" in input_serializer.validated_data:
            reaction, created = set_published_article_reaction(
                user=request.user,
                published_article=input_serializer.validated_data["published_article"],
                reaction_type=input_serializer.validated_data["reaction_type"],
            )
        else:
            reaction, created = set_community_post_reaction(
                user=request.user,
                community_post=input_serializer.validated_data["community_post"],
                reaction_type=input_serializer.validated_data["reaction_type"],
            )
        output_serializer = ReactionReadSerializer(
            instance=reaction,
            context=self.get_serializer_context(),
        )
        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        response_message = "created" if created else "updated"
        response_code = "created" if created else "updated"

        return self.format_success_response(
            message=response_message,
            code=response_code,
            data=output_serializer.data,
            status_code=response_status,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        reaction = self.get_object()
        input_serializer = ReactionWriteSerializer(
            reaction,
            data=request.data,
            partial=partial,
            context=self.get_serializer_context(),
        )
        input_serializer.is_valid(raise_exception=True)
        reaction = update_reaction_type(
            reaction=reaction,
            reaction_type=input_serializer.validated_data["reaction_type"],
        )
        output_serializer = ReactionReadSerializer(
            instance=reaction,
            context=self.get_serializer_context(),
        )

        return self.format_success_response(
            message="updated",
            code="updated",
            data=output_serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @action(
        detail=False,
        methods=["delete"],
        url_path=r"published_articles/(?P<published_article_id>[^/.]+)",
    )
    def clear_published_article(self, request, published_article_id=None):
        published_article = get_object_or_404(PublishedArticle, pk=published_article_id)
        deleted = clear_published_article_reaction(
            user=request.user,
            published_article=published_article,
        )

        return self.format_success_response(
            message="deleted" if deleted else "not reacted",
            code="deleted" if deleted else "not_reacted",
            data={"deleted": deleted},
            status_code=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["delete"],
        url_path=r"community_posts/(?P<community_post_id>[^/.]+)",
    )
    def clear_community_post(self, request, community_post_id=None):
        community_post = get_object_or_404(CommunityPost, pk=community_post_id)
        deleted = clear_community_post_reaction(
            user=request.user,
            community_post=community_post,
        )

        return self.format_success_response(
            message="deleted" if deleted else "not reacted",
            code="deleted" if deleted else "not_reacted",
            data={"deleted": deleted},
            status_code=status.HTTP_200_OK,
        )
