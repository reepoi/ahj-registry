from django.db import connection
from django.urls import reverse
from django.http import HttpRequest
from ahj_app.models import User, Edit, Comment
from fixtures import *
from ahj_app.utils import *
import pytest
import datetime
import requests

@pytest.fixture
def location():
    return {
        'Latitude': {
            'Value': 1
        },
        'Longitude': {
            'Value': 1
        }
    }

@pytest.fixture
def geojson_point():
    return {
            'type': 'Feature',
            'properties': {},
            'geometry': {
                'type': 'Point',
                'coordinates': [-90, 30]
            } 
        }

@pytest.fixture
def geojson_polygon():
    return {
            'geometry': {
                'coordinates': [[[-90, 30], [-90, 30], [-90, 30], [-90, 30]]],
                'type': 'Polygon',
            },
            'properties': {},
            'type': 'Feature'
        }

@pytest.fixture
def feature_collection():
    return {
        'FeatureCollection': {
            'type': 'FeatureCollection',
            'features': [{
                'type': 'Feature',
                'properties': {},
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[
                        [-111.7, 40.97],
                        [-111.6, 40.83],
                        [-111.87, 40.81],
                        [-111.7, 40.97], 
                    ]]
                }
            }]
        }
    }

@pytest.fixture
def mpoly_obj():
    p1 = geosPolygon( ((0, 0), (0, 1), (1, 1), (0, 0)) )
    p2 = geosPolygon( ((1, 1), (1, 2), (2, 2), (1, 1)) )
    mp = MultiPolygon(p1, p2)
    return mp

def create_ahj(ahjpk, ahjid, landArea, ahjLevelCode):
    p1 = geosPolygon( ((0, 0), (0, 1), (1, 1), (0, 0)) )
    p2 = geosPolygon( ((1, 1), (1, 2), (2, 2), (1, 1)) )
    mp = MultiPolygon(p1, p2)
    polygon = Polygon.objects.create(Polygon=mp, LandArea=landArea, WaterArea=1, InternalPLatitude=1, InternalPLongitude=1)
    address = Address.objects.create()
    ahj = AHJ.objects.create(AHJPK=ahjpk, AHJID= ahjid, PolygonID=polygon, AddressID=address, AHJLevelCode=ahjLevelCode)
    return ahj
    

@pytest.mark.django_db
@pytest.mark.parametrize(
   'latVal, longVal, expected_output', [
       (None, None, None),
       (1, None, None),
       (None, 1, None),
       (1, 2, 'POINT(2, 1)'),
   ]
)
def test_get_str_location(latVal, longVal, expected_output):
    location = {
        'Latitude': {
            'Value': latVal
        },
        'Longitude': {
            'Value': longVal
        }
    }
    assert get_str_location(location) == expected_output

@pytest.mark.django_db
@pytest.mark.parametrize(
   'input, expected_output', [
       ({
           'Address': 'University of Utah'
       }, 
       { 'Latitude': { 'Value': 40.8, }, 'Longitude': { 'Value': -111.8 }}
       ),
       ( {}, { 'Latitude': { 'Value': None }, 'Longitude': { 'Value': None }}
       )
   ]
)
def test_get_location(input, expected_output):
    request = HttpRequest()
    request.data = input
    location = get_location(request)
    if location['Latitude']['Value'] is not None and location['Longitude']['Value'] is not None:
        location['Latitude']['Value'] = round(location['Latitude']['Value'], 1) # Round so this test case is future-proof
        location['Longitude']['Value'] = round(location['Longitude']['Value'], 1) 
    assert location == expected_output


@pytest.mark.django_db
@pytest.mark.parametrize(
   'input, expected_output', [
       (None, None),
       ('', ''),
       ('\'e\'\'e\'e\'\'e\'', 'eeee'),
       (';e;;e;e;;e;', 'eeee'),
       (';e\'e;\'e;\'e;', 'eeee'),
       (';;\';;\';\'', ''),
   ]
)
def test_simple_sanitize(input, expected_output):
    assert simple_sanitize(input) == expected_output

@pytest.mark.django_db
@pytest.mark.parametrize(
   'type, val, expected_output', [
       (None, None, ''),
       ('AHJName', None, ''),
       (None, 'Test', ''),
       ('AHJName', 'Test', 'AHJ.AHJName LIKE \'%%Test%%\' AND '),\
   ]
)
def test_get_name_query_cond(type, val, expected_output):
    assert get_name_query_cond(type,val) == expected_output

@pytest.mark.django_db
@pytest.mark.parametrize(
   'type, val, expected_output', [
       ('BuildingCode', ['2018IBC', '2021IBC'], '(AHJ.BuildingCode=\'2018IBC\' OR AHJ.BuildingCode=\'2021IBC\') AND '),
       ('BuildingCode', ['2018IBC'], '(AHJ.BuildingCode=\'2018IBC\') AND '),
       ('BuildingCode', None, ''),
   ]
)
def test_list_query_cond(type, val, expected_output):
    assert get_list_query_cond(type,val) == expected_output

@pytest.mark.django_db
@pytest.mark.parametrize(
   'type, val, expected_output', [
       ('City', 'New York', 'Address.City=\'New York\' AND '),
       ('City', None, ''),
   ]
)
def test_get_basic_user_query_cond(type, val, expected_output):
    assert get_basic_user_query_cond(type,val) == expected_output

@pytest.mark.django_db
@pytest.mark.parametrize(
   'type, val, expected_output', [
       ('BuildingCode', '2018IBC', 'AHJ.BuildingCode=\'2018IBC\' AND '),
       ('City', None, ''),
   ]
)
def test_get_basic_query_cond(type, val, expected_output):
    assert get_basic_query_cond(type,val) == expected_output

@pytest.mark.django_db
def test_point_to_polygon_geojson(geojson_point, geojson_polygon):
    assert point_to_polygon_geojson(geojson_point) == geojson_polygon

@pytest.mark.django_db
def test_get_multipolygon__collection_exists(location, feature_collection):
    request = HttpRequest()
    request.method = 'POST'
    request.data = feature_collection
    resp = get_multipolygon(request, location)
    assert str(resp) == 'MULTIPOLYGON (((-111.7 40.97, -111.6 40.83, -111.87 40.81, -111.7 40.97)), ((1 1, 1 1, 1 1, 1 1)))'

@pytest.mark.django_db
def test_get_multipolygon__collection_does_not_exist(location):
    request = HttpRequest()
    request.data = {}
    assert get_multipolygon(request, location) == None

@pytest.mark.django_db
def test_get_multipolygon_wkt(mpoly_obj):
    assert str(get_multipolygon_wkt(mpoly_obj)) == 'MULTIPOLYGON(((0 0, 0 1, 1 1, 0 0)), ((1 1, 1 2, 2 2, 1 1)))' 

@pytest.mark.django_db
def test_order_ahj_list_AHJLevelCode_PolygonLandArea():
    ahj1 = create_ahj(1, 1, 200, 50)
    ahj2 = create_ahj(2, 2, 10000, 162)
    ahj3 = create_ahj(3, 3, 100, 162)
    ahj4 = create_ahj(4, 4, 200, 60)
    ahjList = [ahj1, ahj2, ahj3, ahj4]
    order_ahj_list_AHJLevelCode_PolygonLandArea(ahjList)
    assert ahjList[0].AHJPK == ahj3.AHJPK # Expected outcome: higher AHJCodeLevel comes first. If tiebreaks, lower land area comes first.
    assert ahjList[1].AHJPK == ahj2.AHJPK
    assert ahjList[2].AHJPK == ahj4.AHJPK
    assert ahjList[3].AHJPK == ahj1.AHJPK

@pytest.mark.django_db
def test_get_public_api_serializer_context():
    assert get_public_api_serializer_context() == {'is_public_view': True}

@pytest.mark.django_db
@pytest.mark.parametrize(
   'input, expected_output', [
       ({ 'Value' : 840}, 840),
       ({}, ''),
       ('BuildingCode', ''),
   ]
)
def test_get_ob_value_primitive(input, expected_output):
    assert get_ob_value_primitive(input) == expected_output

@pytest.mark.django_db
def test_dictfetchall(create_user):
    user1 = create_user(Username='user1')
    user2 = create_user(Username='user2')
    query = "SELECT * FROM User"
    cursor = connection.cursor()
    cursor.execute(query)
    resp = dictfetchall(cursor)
    assert resp[0]['Username'] == 'user1' and resp[1]['Username'] == 'user2' # confirm both dictionaries are user objects  

# Tests for filter ahj:
# no request, no polygon or location objects
# request with no polygon or location object
# request with no polygon but has a location object (location AHJ + AHJ the match request)
# request with a polygon but no location object (all ahjs within the polygon and that match the request)
# just a polygon
# just a location

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

def ahj_filter_create_ahj(ahjpk, ahjid, polygonTuple):
    p1 = geosPolygon(polygonTuple)
    mp = MultiPolygon(p1)
    polygon = Polygon.objects.create(Polygon=mp, LandArea=1, WaterArea=1, InternalPLatitude=1, InternalPLongitude=1)
    address = Address.objects.create()
    ahj = AHJ.objects.create(AHJPK=ahjpk, AHJID= ahjid, PolygonID=polygon, AddressID=address, AHJLevelCode=1)
    StatePolygon.objects.create(PolygonID=polygon)
    return ahj

@pytest.fixture
def ahj_filter_ahjs():
    ahj1 = ahj_filter_create_ahj(1, 1, ((0, 0), (0, 10), (10, 10), (10, 0), (0,0))) # AHJs 1 and 2 are in the same polygon as ahj_filter_polygon
    ahj2 = ahj_filter_create_ahj(2, 2, ((0, 3), (0, 13), (10, 13), (10, 3), (0, 3)))
    ahj3 = ahj_filter_create_ahj(3, 3, ((20, 20), (20, 30), (30, 30), (30, 20), (20,20))) # AHJ 3's polygon is over ahj_filter_location

    ahj4 = ahj_filter_create_ahj(4, 4, ((100, 100), (100, 110), (110, 110), (110, 100), (100, 100))) # AHJ 4 and 5 are found through the request 
    ahj5 = ahj_filter_create_ahj(5, 5, ((100, 100), (100, 110), (110, 110), (110, 100), (100, 100)))
    return ahj1, ahj2, ahj3, ahj4, ahj5

@pytest.mark.django_db
def test_filter_ahjs__no_search_parameters(ahj_filter_ahjs, empty_request_obj):
    ahj1, ahj2, ahj3, ahj4, ahj5 = ahj_filter_ahjs
    assert len(filter_ahjs(empty_request_obj)) == 5 # returns all ahjs if no filtering is done. 

@pytest.mark.django_db
def test_filter_ahjs__only_point_search(ahj_filter_ahjs, empty_request_obj, ahj_filter_location):
    ahj1, ahj2, ahj3, ahj4, ahj5 = ahj_filter_ahjs
    ahj_list = filter_ahjs(empty_request_obj, location=ahj_filter_location)

    assert len(ahj_list) == 1
    assert int(ahj_list[0].AHJID) == ahj3.AHJID

@pytest.mark.django_db
def test_filter_ahjs__only_polygon_search(ahj_filter_ahjs, empty_request_obj, ahj_filter_polygon):
    ahj1, ahj2, ahj3, ahj4, ahj5 = ahj_filter_ahjs
    ahj_list = filter_ahjs(empty_request_obj, polygon=ahj_filter_polygon)

    assert len(ahj_list) == 2 # polygon should overlap with AHJs 1 and 2
    assert all(x in [int(ahj_list[0].AHJID), int(ahj_list[1].AHJID)] for x in [ahj1.AHJID, ahj2.AHJID])