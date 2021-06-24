from rest_framework import permissions

from django.http import HttpRequest
from typing import Any


class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request: HttpRequest, view: Any) -> bool:
        if request.user.is_superuser:
            return True
