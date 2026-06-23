from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from articles.models import ArticlePublication
from drf_std_response import EnvelopeMixin
from posts.models import CommunityPost
from .models import Reaction
from .serializers import ReactionReadSerializer, ReactionWriteSerializer
from .services import (
    clear_community_post_reaction,
    clear_article_publication_reaction,
    set_community_post_reaction,
    set_article_publication_reaction,
    update_reaction_type,
)


class ReactionViewSet(EnvelopeMixin, ModelViewSet):
    queryset = Reaction.objects.select_related(
        "user",
        "target",
        "target__article_publication",
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
        if "article_publication" in input_serializer.validated_data:
            reaction, created = set_article_publication_reaction(
                user=request.user,
                article_publication=input_serializer.validated_data["article_publication"],
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
        url_path=r"article_publications/(?P<article_publication_id>[^/.]+)",
    )
    def clear_article_publication(self, request, article_publication_id=None):
        article_publication = get_object_or_404(ArticlePublication, pk=article_publication_id)
        deleted = clear_article_publication_reaction(
            user=request.user,
            article_publication=article_publication,
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
