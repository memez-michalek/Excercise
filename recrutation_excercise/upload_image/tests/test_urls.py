from django.urls import reverse, resolve

def test_thumbnail_list_url_resolves():
    url = reverse("upload_image:list-thumbnails")
    assert resolve(url).view_name == "upload_image:list-thumbnails"
    assert resolve(url).func.__name__ == "list"

def test_thumbnail_create_url_resolves():
    url = reverse("upload_image:create-thumbnail")
    assert resolve(url).view_name == "upload_image:create-thumbnail"
    assert resolve(url).func.__name__ == "create"

def test_image_detail_url_resolves():
    url = reverse("upload_image:image-detail", kwargs={"pk": 1})
    assert resolve(url).view_name == "upload_image:image-detail"
    assert resolve(url).func.__name__ == "retrieve"

def test_fetch_image_url_resolves():
    url = reverse("upload_image:fetch-image", kwargs={"pk": 1})
    assert resolve(url).view_name == "upload_image:fetch-image"
    assert resolve(url).func.__name__ == "create"

def test_binary_image_detail_url_resolves():
    url = reverse("upload_image:binary-image-detail", kwargs={"slug": "abc"})
    assert resolve(url).view_name == "upload_image:binary-image-detail"
    assert resolve(url).func.__name__ == "retrieve"
