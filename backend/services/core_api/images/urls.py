from django.urls import path

from .views import ImageProcessView, ImageUploadView

urlpatterns = [
    path("", ImageUploadView.as_view(), name="image_upload"),
    path("<uuid:image_id>/process", ImageProcessView.as_view(), name="image_process"),
]
