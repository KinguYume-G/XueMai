"""Reusable authorization helpers for user-owned resources."""

from django.db.models import Q

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrStaff(BasePermission):
    """Allow reads, while restricting object mutations to owners or staff.

    Views may override ``owner_fields`` with a tuple of relationship field
    names.  The defaults cover the ownership conventions used throughout the
    project.  ``User`` objects are treated as self-owned.
    """

    message = "You do not have permission to modify this object."
    default_owner_fields = ("user", "author", "created_by", "posted_by")

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        if obj == user:
            return True

        owner_fields = getattr(view, "owner_fields", self.default_owner_fields)
        for field_name in owner_fields:
            owner_id = getattr(obj, f"{field_name}_id", None)
            if owner_id is not None and owner_id == user.pk:
                return True

            owner = getattr(obj, field_name, None)
            if owner is not None and owner == user:
                return True

        return False


def filter_public_or_owned(queryset, user, owner_field):
    """Return public, published rows plus rows owned by the current user.

    Staff users need an unfiltered administrative view. Resources with a
    ``university`` visibility value are deliberately not exposed here because
    these models do not store a target university against which membership can
    be checked.
    """

    if user and user.is_authenticated:
        if user.is_staff:
            return queryset
        return queryset.filter(
            Q(visibility="public", is_published=True) | Q(**{owner_field: user})
        ).distinct()
    return queryset.filter(visibility="public", is_published=True)
