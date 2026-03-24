from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include


from django.conf import settings


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("pages.urls")),
    path("api/v1/", include("users.urls")),
    path("api/v1/", include("articles.urls")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
