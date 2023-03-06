# from django.shortcuts import render
# Create your views here.
import datetime
import logging
import os
from PIL import Image as PILImage

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.http import HttpResponseForbidden, Http404

from .models import Thumbnail, ThumbnailSize, Link
from .permissions import HasPlan, CanGenerateExpiringLinks
from .serializers import (
    CreateThumbnailSerializer,
    GetThumbnailSerializer,
    ThumbnailLinkSerializer,
    GetLinkSerializer,
    UploadLinkSerializer,
)
from .utils import generate_thumbnail, generate_binary_image

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

class ExpirationLinkViewset(viewsets.GenericViewSet):
    queryset = Link.objects.all()
    #permissions = [HasPlan, IsAuthenticated]
    serializer_class = UploadLinkSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return UploadLinkSerializer
        else:
            return GetLinkSerializer


    def retrieve(self, request, slug=None, *args, **kwargs):
        try: 
            link = Link.objects.get(id=slug)
            if link.expiration_date < datetime.datetime.now():
                link.delete()
                return Http404("Link is expired")
            else:
                serialized = GetThumbnailSerializer(link.thumbnail)
                return Response(data=serialized.data)
        except:
            raise Http404("Link is invalid")


    def create(self, request, *args, **kwargs):
        user = request.user.profile
        plan = user.plan
        thumbnail =request.data.get('thumbnail')
        queryset = Thumbnail.objects.all()
        image = get_object_or_404(
            queryset,
            id=thumbnail,
            owner=user
        )


        time = request.data.get("expiration_date")
        time_delta = datetime.timedelta(seconds=int(time))
        file_path = default_storage.path(image.image.name)
        relative_path = os.path.relpath(file_path, "media")


        file_path = os.path.join("../recrutation_excercise/media/thumbnails/",  image.image.name)
        with open(file_path, 'rb') as file:
            _, height = PILImage.open(file).size

        if not plan.can_generate_expiring_links:
            return HttpResponseForbidden()

       
        binary_image = generate_binary_image(file)
        binary_thumbnail = Thumbnail.objects.create(
            height=height,
            image=binary_image,
            created_at=datetime.datetime.now(),
            owner=user,
        )
        generated_link = Link.objects.create(
            thumbnail=binary_thumbnail,
            expiration_date = datetime.datetime.now() + time_delta,
            is_expired=False,
        )
        serialized = GetLinkSerializer(generated_link)
        return Response(data=serialized.data)




