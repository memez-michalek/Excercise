from django.contrib import admin

from .models import Plan, Profile, Thumbnail, ThumbnailSize

# Register your models here.


@admin.register(Thumbnail)
class ImageAdmin(admin.ModelAdmin):
    list_display = ["id", "height", "image", "created_at", "owner"]
    list_filter = ["height", "created_at", "owner"]
    ordering = ["-created_at", "owner"]
    search_fields = ["owner__user__username"]
    """
    NOTE FOR FUTURE

    Performance considerations for large datasets

    Ordering using ModelAdmin.ordering may cause performance problems as sorting on a large queryset will be slow.

    Also, if your search fields include fields that aren’t indexed by the database,
    you might encounter poor performance on extremely large tables.

    For those cases,
    it’s a good idea to write your own ModelAdmin.get_search_results() implementation using a full-text indexed search.



    """


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "can_view_original_image", "can_generate_expiring_links"]
    list_filter = ["can_view_original_image", "can_generate_expiring_links"]
    search_fields = [
        "name",
    ]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "plan"]
    list_filter = ["plan"]
    search_fields = ["user__username"]


@admin.register(ThumbnailSize)
class ThumbnailSizeAdmin(admin.ModelAdmin):
    list_display = ["height", "plan"]
    list_filter = ["plan"]
    search_fields = [
        "plan__name",
    ]
