from django.urls import reverse, resolve
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.contrib.gis.geos import Polygon as geosPolygon
from ahj_app.models import WebpageToken, APIToken, User, Contact, Address, AHJ, AHJUserMaintains, Polygon
from rest_framework.test import APIClient
from constants import webpageTokenUrls, apiTokenUrls
import datetime
import pytest
import random
import string
import uuid


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db, django_user_model):
    def make_user(**kwargs):
        kwargs['password'] = 'strong-test-pass'
        # If any required field missing, generate it here
        if 'Username' not in kwargs or kwargs['Username'] is None:
            kwargs['Username'] = str(uuid.uuid4())
        if 'Email' not in kwargs or kwargs['Email'] is None:
            kwargs['Email'] = random_char(5) + '@gmail.com'
        user = django_user_model.objects.create_user(**kwargs)
        User.objects.filter(UserID=user.UserID).update(is_active = True)
        return user
    return make_user

@pytest.fixture
def client_with_credentials(db, create_user, api_client):
   user = create_user()
   api_client.force_authenticate(user=user)
   yield api_client
   api_client.force_authenticate(user=None)

@pytest.fixture
def client_with_webpage_credentials(db, create_user, api_client):
   user = create_user()
   #User.objects.filter(UserID=user.UserID).update(is_active = True)
   token = WebpageToken.objects.create(user=user)
   api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
   return api_client

@pytest.fixture
def generate_client_with_webpage_credentials(db, create_user, api_client):
    def generate_client(**kwargs):
        username = kwargs.pop('Username', None)
        email = kwargs.pop('Email', None)
        user = create_user(Username=username, Email=email)
        #User.objects.filter(UserID=user.UserID).update(is_active = True)
        token = WebpageToken.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return api_client
    return generate_client

@pytest.fixture
def client_with_api_credentials(db, create_user, api_client):
   user = create_user()
   #User.objects.filter(UserID=user.UserID).update(is_active = True)
   token = APIToken.objects.create(user=user)
   api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
   return api_client

@pytest.fixture
def generate_client_with_api_credentials(db, create_user, api_client):
    def generate_client(**kwargs):
        username = kwargs.pop('Username', None)
        email = kwargs.pop('Email', None)
        user = create_user(Username=username, Email=email)
        #User.objects.filter(UserID=user.UserID).update(is_active = True)
        token = APIToken.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return api_client
    return generate_client

@pytest.fixture
def ahj_obj(db):
    p1 = geosPolygon( ((0, 0), (0, 1), (1, 1), (0, 0)) )
    p2 = geosPolygon( ((1, 1), (1, 2), (2, 2), (1, 1)) )
    mp = MultiPolygon(p1, p2)
    polygon = Polygon.objects.create(Polygon=mp, LandArea=1, WaterArea=1, InternalPLatitude=1, InternalPLongitude=1)
    address = Address.objects.create()
    ahj = AHJ.objects.create(AHJPK=1, PolygonID=polygon, AddressID=address)
    return ahj 


"""
    Fixture helper methods
"""

def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))