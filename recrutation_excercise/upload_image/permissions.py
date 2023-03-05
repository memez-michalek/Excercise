from rest_framework import permissions


class HasPlan(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "plan")


class CanGenerateExpiringLinks(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.plan.can_generate_expiring_links


class CanViewOriginalImage(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.plan.can_view_original_image
