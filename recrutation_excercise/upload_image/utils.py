import datetime
import logging
import os
import sys
from io import BytesIO

import cv2
# from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image as PILImage

log = logging.getLogger("------->")


def generate_binary_image(image):
    with cv2.imread(image, 2) as img:
        _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        buffer = BytesIO()
        image_format = image.name.split(".")[-1].lower()

        if image_format == "jpg" or image_format == "jpeg":
            img.save(buffer, format="jpeg", quality=85)
        elif image_format == "png":
            img.save(buffer, format="PNG", quality=85)
        else:
            raise ValueError("Unsupported image format")

        filename = f"{os.path.splitext(os.path.basename(image.name)[0])}_{datetime.datetime.now()}_.{format}"
        memory_uploader = InMemoryUploadedFile(
            file=buffer,
            field_name="ImageField",
            name=filename,
            content_type=f"image/{image_format}",
            size=sys.getsizeof(buffer),
            charset=None,
        )
        return memory_uploader


def generate_thumbnail(image, size):
    """Generate a thumbnail of the given size for the given image."""
    img = PILImage.open(image)
    width, height = img.size
    aspect_ratio = width / height

    # Resize the image
    if aspect_ratio > 1:
        # Landscape
        new_width = size * aspect_ratio
        new_height = size
    else:
        # Portrait
        new_width = size
        new_height = size / aspect_ratio
    img = img.resize((int(new_width), int(new_height)), PILImage.ANTIALIAS)

    # Crop the image to the desired size
    x = (new_width - size) / 2
    y = (new_height - size) / 2
    img = img.crop((x, y, x + size, y + size))

    # Save the thumbnail to a BytesIO buffer
    buffer = BytesIO()

    # Check the image format
    image_format = image.name.split(".")[-1].lower()

    # Save the image to the buffer
    if image_format == "jpg" or image_format == "jpeg":
        img.save(buffer, format="JPEG", quality=85)
    elif image_format == "png":
        img.save(buffer, format="PNG", quality=85)
    else:
        raise ValueError("Unsupported image format")

    buffer.seek(0)

    # Create a ContentFile from the BytesIO buffer
    thumbnail_name = (
        os.path.splitext(os.path.basename(image.name))[0]
        + f"_thumbnail_{size}.{image_format}"
    )
    thumbnail = InMemoryUploadedFile(
        buffer,
        "ImageField",
        f"{thumbnail_name}_thumb.{image_format}",
        f"image/{image_format}",
        sys.getsizeof(buffer),
        None,
    )
    # Return the thumbnail
    return thumbnail
