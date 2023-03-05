from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from PIL import Image
import io
from datetime import timedelta
from django.utils import timezone

from .models import Link, Profile, Plan, Thumbnail, ThumbnailSize
from .serializers import GetThumbnailSerializer, LinkSerializer



class ExpirationLinkViewsetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Profile.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )
        self.plan = Plan.objects.create(name="Test Plan", can_generate_expiring_links=True)
        self.user.plan = self.plan
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.image = Image.new("RGB", (100, 100), color="red")
        self.thumbnail = Thumbnail.objects.create(
            height=100,
            image=io.BytesIO(),
            created_at=timezone.now(),
            owner=self.user,
        )

    def test_create_expiring_link_with_valid_plan(self):
        url = reverse("expiration-link-create")
        time = 60
        image = io.BytesIO()
        self.image.save(image, format="PNG")
        data = {"image": image, "time": time}
        response = self.client.post(url, data=data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["thumbnail"]["id"], self.thumbnail.id)
        self.assertEqual(
            response.data["expiration_date"],
            (timezone.now() + timedelta(seconds=time)).isoformat(),
        )
        self.assertFalse(response.data["is_expired"])

    def test_create_expiring_link_with_invalid_plan(self):
        self.plan.can_generate_expiring_links = False
        self.plan.save()
        url = reverse("expiration-link-create")
        time = 60
        image = io.BytesIO()
        self.image.save(image, format="PNG")
        data = {"image": image, "time": time}
        response = self.client.post(url, data=data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_expiring_link_with_expired_plan(self):
        self.plan.can_generate_expiring_links = False
        self.plan.save()
        self.user.plan = None
        self.user.save()
        url = reverse("expiration-link-create")
        time = 60
        image = io.BytesIO()
        self.image.save(image, format="PNG")
        data = {"image": image, "time": time}
        response = self.client.post(url, data=data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_valid_link(self):
        link = Link.objects.create(
            thumbnail=self.thumbnail,
            expiration_date=timezone.now() + timedelta(seconds=60),
            is_expired=False,
        )
        url = reverse("expiration-link-detail", kwargs={"slug": link.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, GetThumbnailSerializer(self.thumbnail).data)

    def test_retrieve_expired_link(self):
        link = Link.objects.create(
            thumbnail=self.thumbnail,
            expiration_date=timezone.now() - timedelta(seconds=60),
            is_expired=True,
        )
        url = reverse("expiration-link-detail", kwargs={"slug": link})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, "Link is expired")
        

class ThumbnailViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpass"
        )
        self.plan = Plan.objects.create(
            name="Test Plan",
            can_view_original_image=True,
            can_generate_expiring_links=True,
        )
        self.thumbnail_size_1 = ThumbnailSize.objects.create(height=100, plan=self.plan)
        self.thumbnail_size_2 = ThumbnailSize.objects.create(height=200, plan=self.plan)
        self.profile = Profile.objects.create(user=self.user, plan=self.plan)

    def test_list_thumbnail(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/thumbnails/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        thumbnail_1 = Thumbnail.objects.create(
            height=100,
            image="path/to/image1.jpg",
            created_at="2022-03-01T10:00:00",
            owner=self.profile,
        )
        thumbnail_2 = Thumbnail.objects.create(
            height=200,
            image="path/to/image2.jpg",
            created_at="2022-03-01T11:00:00",
            owner=self.profile,
        )
        response = self.client.get("/api/thumbnails/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        thumbnail_1_data = response.data[0]
        self.assertEqual(thumbnail_1_data["height"], 100)
        self.assertEqual(thumbnail_1_data["image"], thumbnail_1.image.url)

        thumbnail_2_data = response.data[1]
        self.assertEqual(thumbnail_2_data["height"], 200)
        self.assertEqual(thumbnail_2_data["image"], thumbnail_2.image.url)

    def test_create_thumbnail(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/thumbnails/",
            {
                "image": "path/to/image.jpg",
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data), 2)

        thumbnail_data_1 = response.data[0]
        self.assertEqual(thumbnail_data_1["height"], self.thumbnail_size_1.height)
        self.assertIn("http://localhost:8000/api/image/", thumbnail_data_1["image_link"])

        thumbnail_data_2 = response.data[1]
        self.assertEqual(thumbnail_data_2["height"], self.thumbnail_size_2.height)
        self.assertIn("http://localhost:8000/api/image/", thumbnail_data_2["image_link"])

    def test_retrieve_thumbnail(self):
        self.client.force_authenticate(user=self.user)
        thumbnail = Thumbnail.objects.create(
            height=100,
            image="path/to/image.jpg",
            created_at="2022-03-01T10:00:00",
            owner=self.profile,
        )
        response = self.client.get(f"/api/thumbnails/{thumbnail.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["height"], thumbnail.height)
        self.assertEqual(response.data["image"], thumbnail.image.url)
