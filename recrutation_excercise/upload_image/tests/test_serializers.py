from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Thumbnail, Link
from .serializers import CreateThumbnailSerializer, GetThumbnailSerializer, ThumbnailLinkSerializer, LinkSerializer

class ThumbnailSerializerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.thumbnail = Thumbnail.objects.create(
            height=100,
            image="test.jpg",
            owner="test_owner"
        )

    def test_create_thumbnail_serializer(self):
        data = {
            "height": 200,
            "image": "test2.jpg",
            "owner": "test_owner2"
        }
        serializer = CreateThumbnailSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        thumbnail = serializer.save()

        self.assertEqual(thumbnail.height, data["height"])
        self.assertEqual(thumbnail.image, data["image"])
        self.assertEqual(thumbnail.owner, data["owner"])

    def test_get_thumbnail_serializer(self):
        serializer = GetThumbnailSerializer(self.thumbnail)
        expected_url = "http://localhost:8000" + reverse("upload_image:image-detail", kwargs={"pk": self.thumbnail.pk}).replace("/app/recrutation_excercise/media/", "/media/")
        self.assertEqual(serializer.data["image"], expected_url)

    def test_thumbnail_link_serializer(self):
        serializer = ThumbnailLinkSerializer(self.thumbnail)
        expected_url = f"http://localhost:8000{self.thumbnail.image.url}"
        self.assertEqual(serializer.data["image"], expected_url)


class LinkSerializerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.thumbnail = Thumbnail.objects.create(
            height=100,
            image="test.jpg",
            owner="test_owner"
        )

        self.link = Link.objects.create(
            thumbnail=self.thumbnail,
            expiration_date="2023-03-31"
        )

    def test_create_link_serializer(self):
        data = {
            "thumbnail": self.thumbnail.id,
            "expiration_date": "2023-04-30"
        }
        serializer = LinkSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        link = serializer.save()

        self.assertEqual(link.thumbnail, self.thumbnail)
        self.assertEqual(link.expiration_date, data["expiration_date"])
        self.assertFalse(link.is_expired)

    def test_create_link_serializer_with_expired_date(self):
        data = {
            "thumbnail": self.thumbnail.id,
            "expiration_date": "2022-03-31"
        }
        serializer = LinkSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create_link_serializer_with_invalid_thumbnail(self):
        data = {
            "thumbnail": 999,
            "expiration_date": "2023-04-30"
        }
        serializer = LinkSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create_link_serializer_with_expired_thumbnail(self):
        self.thumbnail.delete()
        data = {
            "thumbnail": self.thumbnail.id,
            "expiration_date": "2023-04-30"
        }
        serializer = LinkSerializer(data=data)
        self.assertFalse(serializer.is_valid())
