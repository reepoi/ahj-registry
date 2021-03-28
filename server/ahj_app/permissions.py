from rest_framework import permissions, status

from django.http import HttpRequest
from typing import Any

from rest_framework.response import Response


class IsSuperuserElseReadOnly(permissions.BasePermission):
    # view: ClassBasedView instance, TODO get this typed
    def has_permission(self, request: HttpRequest, view: Any) -> bool:
        if request.user.is_superuser or request.method == 'GET':
            return True


def check_is_authenticated(request):
    return request.auth is None


def get_not_authenticated_response():
    return Response('Could not authenticate request', status=status.HTTP_401_UNAUTHORIZED)


def check_is_superuser(request):
    return check_is_authenticated(request) and request.user.is_superuser
