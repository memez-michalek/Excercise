import environ
from django.test import TestCase
# from faker import Faker
# from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from recrutation_excercise.users.models import User

env = environ.Env()


class TestThumbnailViewset(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username=env("testing_user"), password=env("testing_password")
        )

    def test_thumbnail_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("http://localhost:8000/api/thumbnails/")
        self.assertEqual(response.status_code, 200)
