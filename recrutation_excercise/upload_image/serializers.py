from django.urls import reverse
from rest_framework import serializers

from .models import Thumbnail, Link


class CreateThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ["id", "image", "created_at", "owner"]


class GetThumbnailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        url = reverse("upload_image:image-detail", kwargs={"pk": obj.pk})
        return "http://localhost:8000" + url.replace(
            "/app/recrutation_excercise/media/", "/media/"
        )

    class Meta:
        model = Thumbnail
        fields = ["id", "height", "image", "created_at", "owner"]


class ThumbnailLinkSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        url = f"http://localhost:8000{obj.image.url}"
        return url

    class Meta:
        model = Thumbnail
        fields = ["id", "height", "image", "created_at", "owner"]


class LinkSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Link
        fields = ["id", "thumbnail", "expiration_date", "is_expired"]