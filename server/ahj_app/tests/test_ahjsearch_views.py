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

@pytest.fixture
def ahj_filter_location():
    return 'POINT(25, 25)'

@pytest.fixture
def empty_request_obj():
    request = HttpRequest()
    request.data = {}
    return request

@pytest.fixture
def ahj_filter_polygon():
    mp = MultiPolygon(geosPolygon(((0, 1), (0, 12), (10, 12), (10, 1), (0, 1))))
    return get_multipolygon_wkt(mp)

def ahj_filter_create_ahj(ahjpk, ahjid, polygonTuple, ahjLevel, BuildingCode=None, ElectricCode=None, AHJName=None):
    p1 = geosPolygon(polygonTuple)
    mp = MultiPolygon(p1)
    polygon = Polygon.objects.create(Polygon=mp, LandArea=1, WaterArea=1, InternalPLatitude=1, InternalPLongitude=1)
    address = Address.objects.create()
    ahj = AHJ.objects.create(AHJPK=ahjpk, AHJID= ahjid, PolygonID=polygon, AddressID=address, AHJLevelCode=ahjLevel, BuildingCode=BuildingCode, ElectricCode=ElectricCode, AHJName=AHJName)
    StatePolygon.objects.create(PolygonID=polygon)
    return ahj

@pytest.fixture
def ahj_filter_ahjs():
    ahjLevel1 = AHJLevelCode.objects.create(AHJLevelCodeID=1, Value=AHJ_LEVEL_CODE_CHOICES[0][0])
    ahjLevel2 = AHJLevelCode.objects.create(AHJLevelCodeID=2, Value=AHJ_LEVEL_CODE_CHOICES[1][0])
    ahjLevel3 = AHJLevelCode.objects.create(AHJLevelCodeID=3, Value=AHJ_LEVEL_CODE_CHOICES[2][0])
    buildingCode = BuildingCode.objects.create(BuildingCodeID=1, Value=BUILDING_CODE_CHOICES[0][0])
    electricCode = ElectricCode.objects.create(ElectricCodeID=1, Value=ELECTRIC_CODE_CHOICES[2][0])

    ahj1 = ahj_filter_create_ahj(1, 1, ((0, 0), (0, 10), (10, 10), (10, 0), (0,0)), ahjLevel1, AHJName='AHJ 1') # AHJs 1 and 2 are in the same polygon as ahj_filter_polygon
    ahj2 = ahj_filter_create_ahj(2, 2, ((0, 3), (0, 13), (10, 13), (10, 3), (0, 3)), ahjLevel2, AHJName='Orange County')
    ahj3 = ahj_filter_create_ahj(3, 3, ((20, 20), (20, 30), (30, 30), (30, 20), (20,20)), ahjLevel3, AHJName='AHJ 3') # AHJ 3's polygon is over ahj_filter_location

    ahj4 = ahj_filter_create_ahj(4, 4, ((100, 100), (100, 110), (110, 110), (110, 100), (100, 100)), ahjLevel1, buildingCode, electricCode, AHJName='AHJ 4') # AHJ 4 and 5 are found through the request 
    ahj5 = ahj_filter_create_ahj(5, 5, ((100, 100), (100, 110), (110, 110), (110, 100), (100, 100)), ahjLevel1, buildingCode, electricCode, AHJName='AHJ 5')
    return ahj1, ahj2, ahj3, ahj4, ahj5

"""@pytest.mark.django_db
def test_webpage_ahj_list__valid_ahj(ahj_obj, client_with_webpage_credentials, ahj_filter_location):
    url = reverse('ahj-private')
    response = client_with_webpage_credentials.post(url, {'Address': 'University of Utah'})
    print(response.data)"""

@pytest.mark.django_db
def test_webpage_ahj_list__no_search_parameters(client_with_webpage_credentials, ahj_filter_ahjs):
    ahj1, ahj2, ahj3, ahj4, ahj5 = ahj_filter_ahjs
    url = reverse('ahj-private')
    response = client_with_webpage_credentials.post(url)
    assert response.data['count'] == 5 # returns all 5 AHJs due to no filtering

@pytest.mark.django_db
def test_filter_ahjs__AHJName_search(ahj_filter_ahjs, ahj_filter_polygon, client_with_webpage_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = ahj_filter_ahjs
    url = reverse('ahj-private')
    response = client_with_webpage_credentials.post(url, {'AHJName': 'Orange County'})
    assert response.data['count'] == 1 
    assert response.data['AHJID'] == 2

@pytest.mark.django_db
def test_filter_ahjs__BuildingCode_search(ahj_filter_ahjs, ahj_filter_polygon, client_with_webpage_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = ahj_filter_ahjs
    url = reverse('ahj-private')
    response = client_with_webpage_credentials.post(url, {'BuildingCode': ["2021IBC"]})
    assert response.data['count'] == 2 

@pytest.mark.django_db
def test_get_single_ahj__valid_ahj(ahj_obj, client_with_webpage_credentials):
    url = reverse('single_ahj')
    response = client_with_webpage_credentials.get(url, {'AHJPK': ahj_obj.AHJPK})
    assert len(response.data) == 1
    assert response.data[0]['AHJPK']['Value'] == ahj_obj.AHJPK

@pytest.mark.django_db
@pytest.mark.parametrize(
   'param', [
       ({}),
       ({'AHJPK': 2}),
   ]
)
def test_get_single_ahj__incorrect_param(param, ahj_obj, client_with_webpage_credentials):
    url = reverse('single_ahj')
    response = client_with_webpage_credentials.get(url, param)
    assert len(response.data) == 0
    assert response.status_code == 200