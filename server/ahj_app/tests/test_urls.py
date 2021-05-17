from django.urls import reverse, resolve
import pytest

def test_ahj_url(self):
    path = reverse('ahj-public')
    assert resolve(path).view_name == 'ahj-public'