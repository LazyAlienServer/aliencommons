from rest_framework import routers

from .views import ContentReportViewSet, UserReportViewSet


router = routers.SimpleRouter()
router.register(r"content_reports", ContentReportViewSet, basename="content_report")
router.register(r"user_reports", UserReportViewSet, basename="user_report")

urlpatterns = []
urlpatterns += router.urls

