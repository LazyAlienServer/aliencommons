from rest_framework import status

from core.utils.permissions import is_moderator
from core.views.viewsets import MyModelViewSet

from .models import ContentReport, UserReport
from .permissions import ReportPermission
from .serializers import (
    ContentReportReadSerializer,
    ContentReportWriteSerializer,
    ReportModerationSerializer,
    UserReportReadSerializer,
    UserReportWriteSerializer,
)
from .services import create_content_report, create_user_report, moderate_report


class BaseReportViewSet(MyModelViewSet):
    permission_classes = [ReportPermission]
    moderation_serializer_class = ReportModerationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if is_moderator(self.request.user):
            return queryset
        return queryset.filter(reporter=self.request.user)

    def get_serializer_class(self):
        if self.action in ("create",):
            return self.write_serializer_class
        if self.action in ("update", "partial_update"):
            return self.moderation_serializer_class
        return self.read_serializer_class

    def update(self, request, *args, **kwargs):
        report = self.get_object()
        serializer = ReportModerationSerializer(
            report,
            data=request.data,
            partial=kwargs.pop("partial", False),
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        report = moderate_report(
            report=report,
            moderator=request.user,
            status=serializer.validated_data["status"],
            resolution_note=serializer.validated_data.get("resolution_note", report.resolution_note),
        )
        output_serializer = self.read_serializer_class(
            instance=report,
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


class ContentReportViewSet(BaseReportViewSet):
    queryset = ContentReport.objects.select_related(
        "reporter",
        "target",
        "resolved_by",
    )
    read_serializer_class = ContentReportReadSerializer
    write_serializer_class = ContentReportWriteSerializer

    def create(self, request, *args, **kwargs):
        input_serializer = ContentReportWriteSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        input_serializer.is_valid(raise_exception=True)
        report = create_content_report(
            reporter=request.user,
            target=input_serializer.validated_data["target"],
            reason=input_serializer.validated_data["reason"],
            description=input_serializer.validated_data.get("description", ""),
        )
        output_serializer = ContentReportReadSerializer(
            instance=report,
            context=self.get_serializer_context(),
        )

        return self.format_success_response(
            message="created",
            code="created",
            data=output_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )


class UserReportViewSet(BaseReportViewSet):
    queryset = UserReport.objects.select_related(
        "reporter",
        "reported_user",
        "resolved_by",
    )
    read_serializer_class = UserReportReadSerializer
    write_serializer_class = UserReportWriteSerializer

    def create(self, request, *args, **kwargs):
        input_serializer = UserReportWriteSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        input_serializer.is_valid(raise_exception=True)
        report = create_user_report(
            reporter=request.user,
            reported_user=input_serializer.validated_data["reported_user"],
            reason=input_serializer.validated_data["reason"],
            description=input_serializer.validated_data.get("description", ""),
        )
        output_serializer = UserReportReadSerializer(
            instance=report,
            context=self.get_serializer_context(),
        )

        return self.format_success_response(
            message="created",
            code="created",
            data=output_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

