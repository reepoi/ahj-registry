import rest_framework.authentication
from .models import WebpageToken, APIToken


class WebpageTokenAuth(rest_framework.authentication.TokenAuthentication):
    model = WebpageToken


class APITokenAuth(rest_framework.authentication.TokenAuthentication):
    model = APIToken
