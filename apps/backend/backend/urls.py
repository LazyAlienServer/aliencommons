from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include


from django.conf import settings


urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/", include("users.urls")),
    path("v1/", include("articles.urls")),
    path("v1/", include("bookmarks.urls")),
    path("v1/", include("comments.urls")),
    path("v1/", include("reactions.urls")),
    path("v1/", include("reports.urls")),
    path("v1/", include("notifications.urls")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
