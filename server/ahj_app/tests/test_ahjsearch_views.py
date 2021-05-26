from django.db import connection
from django.urls import reverse
from django.http import HttpRequest
from ahj_app.models import User, Edit, Comment
from ahj_app.models_field_enums import *
from fixtures import *
from ahj_app.utils import *
import pytest
import datetime
import requests

"""
    Only Public AHJ Search Tests
"""
@pytest.mark.django_db
def test_ahj_geo_address__missing_address(client_with_credentials):
    url = reverse('ahj-geo-address')
    response = client_with_credentials.post(url)
    assert response.status_code == 400

@pytest.mark.django_db
def test_ahj_geo_address__invalid_address(client_with_credentials):
    url = reverse('ahj-geo-address')
    response = client_with_credentials.post(url, {'Address': {'AddrLine1': {'Value': '112 Baker St'}, 'AddrLine3': {''}}}, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_ahj_geo_address__valid_address_format(client_with_credentials):
    url = reverse('ahj-geo-address')
    response = client_with_credentials.post(url, {'AddrLine1': {'Value': '112 Baker St'}, 'City': {'Value': 'Salt Lake City'}}, format='json')
    assert response.status_code == 200
    response = client_with_credentials.post(url, {'Address': {'AddrLine1': {'Value': '112 Baker St'}, 'City': {'Value': 'Salt Lake City'}}}, format='json')
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_address__both_params_with_outdated_address_format(client_with_credentials):
    url = reverse('ahj-geo-address')
    response = client_with_credentials.post(url, {'ahjs_to_search': ['ID1', 'ID2'], 'AddrLine1': {'Value': '112 Baker St'}, 'City': {'Value': 'Salt Lake City'}}, format='json')
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_address__both_params(client_with_credentials):
    url = reverse('ahj-geo-address')
    response = client_with_credentials.post(url, {'ahjs_to_search': ['ID1', 'ID2'], 'Address': {'AddrLine1': {'Value': '112 Baker St'}}}, format='json')
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_location__valid_location_format(client_with_credentials):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url, { 'Latitude': { 'Value': '25' }, 'Longitude': { 'Value': '25' }}, format='json')
    assert response.status_code == 200
    response = client_with_credentials.post(url, {'Location': { 'Latitude': { 'Value': '25' }, 'Longitude': { 'Value': '25' }}}, format='json')
    assert response.status_code == 200

@pytest.mark.django_db
def test_ahj_geo_location__missing_lat_or_long(client_with_credentials):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url, {'Location': { 'Latitude': { 'Value': '25' }}}, format='json')
    assert response.status_code == 400
    response = client_with_credentials.post(url, {'Location': {'Longitude': { 'Value': '25' }}}, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_ahj_geo_location__missing_location(client_with_credentials):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url)
    assert response.status_code == 400

@pytest.mark.django_db
def test_ahj_geo_location__invalid_location_format(client_with_credentials):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url, {'Location': {'Latitude': '25', 'Longitude': '25'}}, format='json')
    assert response.status_code == 400