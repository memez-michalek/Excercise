from django.db import models

from recrutation_excercise.users.models import User

# Create your models here.


class Plan(models.Model):
    name = models.CharField(max_length=40)
    can_view_original_image = models.BooleanField(default=False)
    can_generate_expiring_links = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ThumbnailSize(models.Model):
    height = models.IntegerField()
    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name="thumbnail_size"
    )

    def __str__(self):
        return f"thumbnail height: {self.height} plan: {self.plan}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"profile user: {self.user} with plan: {self.plan}"


class Thumbnail(models.Model):
    height = models.IntegerField()
    image = models.ImageField(upload_to="thumbnails/")
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="thumbnail_image"
    )

    def __str__(self):
        return f"thumbnail: {self.id} with height: {self.height}"
