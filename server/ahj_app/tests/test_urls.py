from django.urls import reverse, resolve
from constants import webpageTokenUrls, apiTokenUrls
import pytest

@pytest.mark.parametrize('urlName, args', webpageTokenUrls + apiTokenUrls)
def test_url_name_has_path(urlName, args):
    if (args):
        path = reverse(urlName, kwargs=args)
    else:
        path = reverse(urlName)
    assert resolve(path).view_name == urlName