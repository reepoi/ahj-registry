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

def ahj_filter_create_ahj(ahjpk, ahjid, polygonTuple, ahjLevel, AHJCode, BuildingCode=None, ElectricCode=None, AHJName=None):
    p1 = geosPolygon(polygonTuple)
    mp = MultiPolygon(p1)
    polygon = Polygon.objects.create(Polygon=mp, LandArea=1, WaterArea=1, InternalPLatitude=1, InternalPLongitude=1)
    address = Address.objects.create()
    ahj = AHJ.objects.create(AHJPK=ahjpk, AHJID= ahjid, AHJCode=AHJCode, PolygonID=polygon, AddressID=address, AHJLevelCode=ahjLevel, BuildingCode=BuildingCode, ElectricCode=ElectricCode, AHJName=AHJName)
    StatePolygon.objects.create(PolygonID=polygon)
    return ahj

@pytest.fixture
def list_of_ahjs():
    ahjLevel1 = AHJLevelCode.objects.create(AHJLevelCodeID=1, Value=AHJ_LEVEL_CODE_CHOICES[0][0])
    ahjLevel2 = AHJLevelCode.objects.create(AHJLevelCodeID=2, Value=AHJ_LEVEL_CODE_CHOICES[1][0])
    ahjLevel3 = AHJLevelCode.objects.create(AHJLevelCodeID=3, Value=AHJ_LEVEL_CODE_CHOICES[2][0])
    buildingCode = BuildingCode.objects.create(BuildingCodeID=1, Value=BUILDING_CODE_CHOICES[0][0])
    buildingCode2 = BuildingCode.objects.create(BuildingCodeID=2, Value=BUILDING_CODE_CHOICES[1][0])
    electricCode = ElectricCode.objects.create(ElectricCodeID=1, Value=ELECTRIC_CODE_CHOICES[0][0])

    ahj1 = ahj_filter_create_ahj(1, 1, ((0, 0), (0, 10), (10, 10), (10, 0), (0,0)), ahjLevel1, 'Code1', buildingCode2, AHJName='AHJ 1') # AHJs 1 and 2 are in the same polygon as ahj_filter_polygon
    ahj2 = ahj_filter_create_ahj(2, 'f97ea81a-f9c4-4195-889e-ad414b736ce5', ((0, 3), (0, 13), (10, 13), (10, 3), (0, 3)), ahjLevel2, 'CA-0686300', AHJName='Orange County' )
    ahj3 = ahj_filter_create_ahj(3, 3, ((20, 20), (20, 30), (30, 30), (30, 20), (20,20)), ahjLevel3, 'UT-0681820', AHJName='AHJ 3') # AHJ 3's polygon is over ahj_filter_location

    ahj4 = ahj_filter_create_ahj(4, 4, ((100, 100), (100, 110), (110, 110), (110, 100), (100, 100)), ahjLevel1, 'Code 4', buildingCode, electricCode, AHJName='AHJ 4') # AHJ 4 and 5 are found through the request 
    ahj5 = ahj_filter_create_ahj(5, 5, ((100, 100), (100, 110), (110, 110), (110, 100), (100, 100)), ahjLevel1, 'Code 5', buildingCode, electricCode, AHJName='AHJ 5')
    return ahj1, ahj2, ahj3, ahj4, ahj5

"""
    Public and Private AHJ Search Tests
"""

@pytest.mark.parametrize(
   'url_name', [
       ('ahj-private'),
       ('ahj-public')
   ])
@pytest.mark.django_db
def test_webpage_ahj_list__no_search_parameters(url_name, client_with_credentials, list_of_ahjs):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url)
    assert response.data['count'] == 5 # returns all 5 AHJs due to no filtering

@pytest.mark.parametrize(
   'url_name, payload', [
       ('ahj-private', {'AHJName': 'Orange County'}),
       ('ahj-public', {'AHJName': { 'Value': 'Orange County'}})
   ])
@pytest.mark.django_db
def test_ahj_list__AHJName_search(url_name, payload, list_of_ahjs, ahj_filter_polygon, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url, payload, format='json')
    assert response.data['count'] == 1 
    if url_name == 'ahj-public': assert response.data['AuthorityHavingJurisdictions'][0]['AHJCode']['Value'] == 'CA-0686300' # verify only the ahj2 was returned
    else: assert response.data['results']['ahjlist'][0]['AHJCode']['Value'] == 'CA-0686300'
    

@pytest.mark.parametrize(
   'url_name, payload', [
       ('ahj-private', {'AHJID': 'f97ea81a-f9c4-4195-889e-ad414b736ce5'}),
       ('ahj-public', {'AHJID': {'Value': 'f97ea81a-f9c4-4195-889e-ad414b736ce5'}})
   ])
@pytest.mark.django_db
def test_ahj_list__AHJID_search(url_name, payload, list_of_ahjs, ahj_filter_polygon, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url, payload, format='json')
    assert response.data['count'] == 1 
    if url_name == 'ahj-public': assert response.data['AuthorityHavingJurisdictions'][0]['AHJCode']['Value'] == 'CA-0686300' # verify only the ahj2 was returned
    else: assert response.data['results']['ahjlist'][0]['AHJCode']['Value'] == 'CA-0686300'

@pytest.mark.parametrize(
   'url_name, payload', [
       ('ahj-private', {'AHJCode': 'CA-0686300'}),
       ('ahj-public', {'AHJCode': {'Value': 'CA-0686300'}})
   ])
@pytest.mark.django_db
def test_ahj_list__AHJCode_search(url_name, payload, list_of_ahjs, ahj_filter_polygon, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url, payload, format='json')
    assert response.data['count'] == 1 
    if url_name == 'ahj-public': assert response.data['AuthorityHavingJurisdictions'][0]['AHJCode']['Value'] == 'CA-0686300' # verify only the ahj2 was returned
    else: assert response.data['results']['ahjlist'][0]['AHJCode']['Value'] == 'CA-0686300'

@pytest.mark.parametrize(
   'url_name, payload', [
       ('ahj-private', {'AHJLevelCode': '040'}),
       ('ahj-public', {'AHJLevelCode': {'Value': '040'}})
   ])
@pytest.mark.django_db
def test_ahj_list__AHJLevelCode_search(url_name, payload, list_of_ahjs, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url, payload, format='json')
    assert response.data['count'] == 3

@pytest.mark.parametrize(
   'url_name, payload', [
       ('ahj-private', {'AHJLevelCode': '040'}),
       ('ahj-public', {'AHJLevelCode': {'Value': '040'}})
   ])
@pytest.mark.django_db
def test_ahj_list__AHJLevelCode_search(url_name, payload, list_of_ahjs, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url, payload, format='json')
    assert response.data['count'] == 3

@pytest.mark.parametrize(
   'url_name, payload', [
       ('ahj-private', { "BuildingCode": [ "2021IBC" ],  "ElectricCode": [  "2020NEC"  ]}),
       ('ahj-public', { 'BuildingCodes': [ { 'Value': '2021IBC'} ],  'ElectricCodes': [  { 'Value':'2020NEC'}  ]})
   ])
@pytest.mark.django_db
def test_ahj_list__BuildingCode_search(url_name, payload, list_of_ahjs, client_with_credentials):
    ahj1, ahj2, ahj3, ahj4, ahj5 = list_of_ahjs
    url = reverse(url_name)
    response = client_with_credentials.post(url, payload, format='json')
    assert response.data['count'] == 2 

"""
    Only Private AHJ Search Tests
"""
@pytest.mark.django_db
def test_get_single_ahj__valid_ahj(ahj_obj, client_with_credentials):
    url = reverse('single_ahj')
    response = client_with_credentials.get(url, {'AHJPK': ahj_obj.AHJPK})
    assert len(response.data) == 1
    assert response.data[0]['AHJPK']['Value'] == ahj_obj.AHJPK

@pytest.mark.django_db
@pytest.mark.parametrize(
   'param', [
       ({}),
       ({'AHJPK': 2}),
   ]
)
def test_get_single_ahj__incorrect_param(param, ahj_obj, client_with_credentials):
    url_name = reverse('single_ahj')
    response = client_with_credentials.get(url_name, param)
    assert len(response.data) == 0
    assert response.status_code == 200

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

@pytest.mark.django_db
def test_ahj_geo_location__normal_use(client_with_credentials):
    url = reverse('ahj-geo-location')
    response = client_with_credentials.post(url, {'Location': {
        'Latitude': {
            'Value': '25'
        },
        'Longitude': {
            'Value': '25'
        }
    }}, format='json')
    print(response.data)
    assert response.data['count'] == 1
    assert response.data['results']['ahjlist'][0]['AHJCode']['Value'] == 'UT-0681820'
    assert response.status_code == 200