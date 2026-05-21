from core.services.content_targets import get_or_create_published_article_target
from core.tests.factories import (
    create_community_post,
    create_content_report,
    create_published_article,
    create_source_article,
    create_user,
    create_user_report,
)
from core.tests.testcases import BaseTestCase
from reports.models import ContentReport, UserReport


class ReportModelTests(BaseTestCase):
    def setUp(self):
        self.reporter = create_user(username="reporter")
        self.reported_user = create_user(username="reported")
        self.article = create_source_article(title="Guide")
        self.published = create_published_article(self.article, title=self.article.title)

    def test_content_report_string_representation(self):
        target = get_or_create_published_article_target(self.published)
        report = create_content_report(self.reporter, target)

        self.assertEqual(str(report), f"Content report {report.id}")

    def test_user_report_string_representation(self):
        report = create_user_report(self.reporter, self.reported_user)

        self.assertEqual(str(report), f"User report {report.id}")

    def test_content_report_keeps_snapshot_when_target_is_deleted(self):
        target = get_or_create_published_article_target(self.published)
        report = create_content_report(self.reporter, target)

        self.published.delete()

        report.refresh_from_db()
        self.assertIsNone(report.target)
        self.assertEqual(report.snapshot["title"], "Guide")
        self.assertTrue(ContentReport.objects.filter(id=report.id).exists())

    def test_content_report_snapshots_community_post_mentions(self):
        post = create_community_post(
            author=self.reported_user,
            body="Hello {{mention:0}}",
            mentions=[str(self.reporter.id)],
        )

        report = create_content_report(self.reporter, post.content_target)

        self.assertEqual(report.snapshot["target_object_id"], str(post.id))
        self.assertEqual(report.snapshot["mentions"], [str(self.reporter.id)])
        self.assertEqual(
            report.snapshot["render_body"],
            "Hello [@reporter](http://testserver/users/reporter)",
        )

    def test_user_report_keeps_snapshot_when_reported_user_is_deleted(self):
        report = create_user_report(self.reporter, self.reported_user)

        self.reported_user.delete()

        report.refresh_from_db()
        self.assertIsNone(report.reported_user)
        self.assertEqual(report.snapshot["username"], "reported")
        self.assertTrue(UserReport.objects.filter(id=report.id).exists())
