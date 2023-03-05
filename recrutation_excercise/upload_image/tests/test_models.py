import factory
from django.test import TestCase
from faker import Faker
from upload_image.models import Plan, Thumbnail, ThumbnailSize

from recrutation_excercise.users.models import User

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    name = factory.LazyFunction(lambda: fake.simple_profile()["name"])
    username = factory.LazyFunction(lambda: fake.simple_profile()["username"])


class PlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Plan

    name = fake.word()
    can_view_original_image = fake.boolean()
    can_generate_expiring_links = fake.boolean()


class ThumbailSizeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ThumbnailSize

    height = fake.random_number(digits=3)
    plan = factory.SubFactory(PlanFactory)


"""
class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    plan = factory.SubFactory(PlanFactory)
"""


class ThumbnailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Thumbnail

    height = factory.Faker("pyint", min_value=100, max_value=400)
    image = factory.django.ImageField(color="red")
    created_at = factory.Faker("date_time")
    # solution provided by docs
    owner = factory.SubFactory(UserFactory)


class TestThumbnail(TestCase):
    def setUp(self):
        self.thumbnail = ThumbnailFactory()

    def test_get_thumbnail_object_str(self):
        self.assertEqual(
            f"thumbnail: {self.thumbnail.id} with height: {self.thumbnail.height}",
            self.thumbnail.__str__(),
        )


class TestPlan(TestCase):
    def setUp(self) -> None:
        self.plan = PlanFactory()

    def test_get_plan_object_str(self):
        self.assertEqual(self.plan.name, self.plan.__str__())


class TestThumbnailSize(TestCase):
    def setUp(self):
        self.thumbnail_sizes = ThumbailSizeFactory()

    def test_get_thumbnail_size_object_str(self):
        self.assertEqual(
            f"thumbnail height: {self.thumbnail_sizes.height} plan: {self.thumbnail_sizes.plan}",
            self.thumbnail_sizes.__str__(),
        )


"""
class TestProfile(TestCase):
    def setUp(self):
        self.profile = ProfileFactory()

    def test_get_thumbnail_size_object_str(self):
        self.assertEqual(
            f"profile user: {self.profile.user} with plan: {self.profile.plan}",
            self.profile.__str__(),
        )

    def test_automatic_profile_creation(self):
        pass
"""
