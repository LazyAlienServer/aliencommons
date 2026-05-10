from django.urls import reverse

from rest_framework import status

from core.services.content_targets import get_or_create_published_article_target
from core.tests.factories import (
    create_content_report,
    create_moderator,
    create_published_article,
    create_source_article,
    create_user,
    create_user_report,
)
from core.tests.testcases import BaseAPITestCase
from reports.models import ContentReport, UserReport


class ContentReportViewTests(BaseAPITestCase):
    def setUp(self):
        self.reporter = create_user(username="reporter")
        self.other_user = create_user(username="other-user")
        self.moderator = create_moderator(username="moderator")
        self.article = create_source_article(title="Guide")
        self.published = create_published_article(self.article, title=self.article.title)
        self.target = get_or_create_published_article_target(self.published)

    def test_user_can_create_content_report(self):
        self.authenticate(self.reporter)
        response = self.post_json(
            reverse("content_report-list"),
            {
                "target": str(self.target.id),
                "reason": ContentReport.ReportReason.SPAM,
                "description": "Looks like spam",
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assert_uuid_equal(response.data["data"]["reporter"], self.reporter.id)
        self.assert_uuid_equal(response.data["data"]["target"], self.target.id)
        self.assertEqual(response.data["data"]["snapshot"]["title"], "Guide")
        self.assertEqual(ContentReport.objects.count(), 1)

    def test_user_only_lists_own_content_reports(self):
        own_report = create_content_report(self.reporter, self.target)
        create_content_report(self.other_user, self.target)

        self.authenticate(self.reporter)
        response = self.get_json(reverse("content_report-list"))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
        )
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assert_uuid_equal(response.data["data"]["results"][0]["id"], own_report.id)

    def test_moderator_lists_all_content_reports(self):
        create_content_report(self.reporter, self.target)
        create_content_report(self.other_user, self.target)

        self.authenticate(self.moderator)
        response = self.get_json(reverse("content_report-list"))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
        )
        self.assertEqual(len(response.data["data"]["results"]), 2)

    def test_moderator_can_update_content_report_status(self):
        report = create_content_report(self.reporter, self.target)

        self.authenticate(self.moderator)
        response = self.patch_json(
            reverse("content_report-detail", args=[report.id]),
            {
                "status": ContentReport.ReportStatus.RESOLVED,
                "resolution_note": "Handled",
            },
        )

        report.refresh_from_db()
        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="updated",
        )
        self.assertEqual(report.status, ContentReport.ReportStatus.RESOLVED)
        self.assertEqual(report.resolution_note, "Handled")
        self.assertEqual(report.resolved_by, self.moderator)
        self.assertIsNotNone(report.resolved_at)

    def test_non_moderator_cannot_update_content_report_status(self):
        report = create_content_report(self.reporter, self.target)

        self.authenticate(self.reporter)
        response = self.patch_json(
            reverse("content_report-detail", args=[report.id]),
            {
                "status": ContentReport.ReportStatus.RESOLVED,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserReportViewTests(BaseAPITestCase):
    def setUp(self):
        self.reporter = create_user(username="reporter")
        self.reported_user = create_user(username="reported")
        self.other_user = create_user(username="other-user")
        self.moderator = create_moderator(username="moderator")

    def test_user_can_create_user_report(self):
        self.authenticate(self.reporter)
        response = self.post_json(
            reverse("user_report-list"),
            {
                "reported_user": str(self.reported_user.id),
                "reason": UserReport.ReportReason.HARASSMENT,
                "description": "Profile signature is abusive",
            },
        )

        self.assert_success_response(
            response,
            status_code=status.HTTP_201_CREATED,
            code="created",
        )
        self.assert_uuid_equal(response.data["data"]["reporter"], self.reporter.id)
        self.assert_uuid_equal(response.data["data"]["reported_user"], self.reported_user.id)
        self.assertEqual(response.data["data"]["snapshot"]["username"], "reported")
        self.assertEqual(UserReport.objects.count(), 1)

    def test_user_cannot_report_self(self):
        self.authenticate(self.reporter)
        response = self.post_json(
            reverse("user_report-list"),
            {
                "reported_user": str(self.reporter.id),
                "reason": UserReport.ReportReason.OTHER,
            },
        )

        self.assert_error_response(
            response,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(UserReport.objects.count(), 0)

    def test_user_only_lists_own_user_reports(self):
        own_report = create_user_report(self.reporter, self.reported_user)
        create_user_report(self.other_user, self.reported_user)

        self.authenticate(self.reporter)
        response = self.get_json(reverse("user_report-list"))

        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="listed",
        )
        self.assertEqual(len(response.data["data"]["results"]), 1)
        self.assert_uuid_equal(response.data["data"]["results"][0]["id"], own_report.id)

    def test_moderator_can_update_user_report_status(self):
        report = create_user_report(self.reporter, self.reported_user)

        self.authenticate(self.moderator)
        response = self.patch_json(
            reverse("user_report-detail", args=[report.id]),
            {
                "status": UserReport.ReportStatus.REJECTED,
                "resolution_note": "No violation",
            },
        )

        report.refresh_from_db()
        self.assert_success_response(
            response,
            status_code=status.HTTP_200_OK,
            code="updated",
        )
        self.assertEqual(report.status, UserReport.ReportStatus.REJECTED)
        self.assertEqual(report.resolved_by, self.moderator)
        self.assertIsNotNone(report.resolved_at)

