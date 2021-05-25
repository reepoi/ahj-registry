from django.urls import reverse
from fixtures import *
from constants import *
import pytest

def createUrl(urlName, args):
    if (args):
        url = reverse(urlName, kwargs=args)
    else:
        url = reverse(urlName)
    return url

"""
    Access Views while unauthorized
"""

@pytest.mark.django_db
@pytest.mark.parametrize('urlName, args', webpageTokenUrls + apiTokenUrls)
def test_unauthorized_requests(urlName, args, api_client):
    url = createUrl(urlName, args)
    response = api_client.get(url) # not all views are GET, but response will be 401 if user is not authorized
    assert response.status_code == 401

@pytest.mark.django_db
@pytest.mark.parametrize('urlName, args', apiTokenUrls)
def test_APIToken_endpoints_using_WebpageToken(urlName, args, client_with_webpage_credentials):
    url = createUrl(urlName, args)
    response = client_with_webpage_credentials.get(url) # not all views are GET, but response will be 401 if user is not authorized
    assert response.status_code == 401

@pytest.mark.django_db
@pytest.mark.parametrize('urlName, args', webpageTokenUrls)
def test_WebpageToken_endpoints_using_APIToken(urlName, args, client_with_api_credentials):
    url = createUrl(urlName, args)
    response = client_with_api_credentials.get(url) # not all views are GET, but response will be 401 if user is not authorized
    assert response.status_code == 401