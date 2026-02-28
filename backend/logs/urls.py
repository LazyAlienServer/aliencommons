from django.urls import path

from .views import (
    FrontendLogCreateView
)


urlpatterns = [
    path('collect/', FrontendLogCreateView.as_view(), name='frontend_logs_bulkcreate'),
]
