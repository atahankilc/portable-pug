from django.urls import path
from .views import UploadView, StatusView, ResultsView

urlpatterns = [
    path("upload/", UploadView.as_view(), name="ml-upload"),
    path("status/<str:task_id>/", StatusView.as_view(), name="ml-status"),
    path("results/", ResultsView.as_view(), name="ml-results"),
]
