# from django.shortcuts import render
# Create your views here.
import datetime
import logging

from django.shortcuts import get_object_or_404
from PIL import Image as PILImage
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Thumbnail, ThumbnailSize
from .permissions import HasPlan
from .serializers import (
    CreateThumbnailSerializer,
    GetThumbnailSerializer,
    ThumbnailLinkSerializer,
)
from .utils import generate_thumbnail

log = logging.getLogger("########################>")


class ThumbnailViewSet(viewsets.GenericViewSet):
    queryset = Thumbnail.objects.all()
    serializer_class = GetThumbnailSerializer
    permissions = [HasPlan, IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateThumbnailSerializer
        else:
            return GetThumbnailSerializer

    def list(self, request, *args, **kwargs):
        return_thumbnails = []
        users_plan = request.user.profile.plan
        for size in ThumbnailSize.objects.filter(plan=users_plan):
            height = int(size.height)
            thumbnails = Thumbnail.objects.filter(
                height=height, owner=request.user.profile
            )
            return_thumbnails.extend(thumbnails)

        serialized = self.serializer_class(return_thumbnails, many=True)
        return Response(data=serialized.data)

    def create(self, request, *args, **kwargs):
        user = request.user.profile
        plan = user.plan
        image = request.data.get("image")

        log.debug(image)
        sizes = ThumbnailSize.objects.filter(plan=plan)
        return_thumbnails = {}
        return_thumbnail_objects = []

        for size in sizes:
            height = int(size.height)
            thumbnail = generate_thumbnail(image, height)

            generated_thumbnail = Thumbnail.objects.create(
                height=height,
                image=thumbnail,
                created_at=datetime.datetime.now,
                owner=user,
            )
            print(generated_thumbnail.image.url)
            return_thumbnail_objects.append(generated_thumbnail)
            log.debug(generated_thumbnail)

            return_thumbnails["height"] = height
            return_thumbnails[
                "image_link"
            ] = f"http://localhost:8000/api/image/{generated_thumbnail.id}/"

        if plan.can_view_original_image:
            _, height = PILImage.open(image).size

            generated_thumbnail = Thumbnail.objects.create(
                height=height, image=image, created_at=datetime.datetime.now, owner=user
            )
            return_thumbnail_objects.append(generate_thumbnail)

            return_thumbnails["height"] = height
            return_thumbnails[
                "image_link"
            ] = f"http://localhost:8000/api/image/{generated_thumbnail.id}"

        print(return_thumbnail_objects)
        serialized = GetThumbnailSerializer(return_thumbnail_objects, many=True)

        return Response(data=serialized.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        user = request.user.profile
        queryset = Thumbnail.objects.all()

        image = get_object_or_404(queryset, pk=pk, owner=user)
        print(image)
        print(image.image.url)
        serialized = ThumbnailLinkSerializer(
            image,
        )
        return Response(data=serialized.data)
