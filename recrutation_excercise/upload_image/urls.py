from django.urls import path

from recrutation_excercise.upload_image.views import ThumbnailViewSet

app_name = "upload_image"

urlpatterns = [
    path(
        "thumbnails/", ThumbnailViewSet.as_view({"get": "list"}), name="list-thumbnails"
    ),
    path(
        "thumbnails/create/",
        ThumbnailViewSet.as_view({"post": "create"}),
        name="create-thumbnail",
    ),
    path(
        "image/<int:pk>/",
        ThumbnailViewSet.as_view({"get": "retrieve"}),
        name="image-detail",
    ),
]
