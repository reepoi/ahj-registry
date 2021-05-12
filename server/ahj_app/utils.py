import json

from django.apps import apps

from .serializers import *
import googlemaps
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon


gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_KEY)


def get_ob_value_primitive(ob_json, field_name, throw_exception=True, exception_return_value=None):
    try:
        if isinstance(ob_json[field_name], list):
            values = []
            for o in ob_json[field_name]:
                values.append(o['Value'])
            return values
        return ob_json[field_name]['Value']
    except (TypeError, KeyError):
        if throw_exception:
            raise ValueError(f'Missing \'Value\' key for Orange Button field \'{field_name}\'')
        return exception_return_value


def get_str_location(location):
    lng, lat = get_ob_value_primitive(location, 'Longitude'), get_ob_value_primitive(location, 'Latitude')
    try:
        if lat is not None and lng is not None:
            return 'POINT(' + str(float(lng)) + ', ' + str(float(lat)) + ')'
        return None
    except ValueError:
        raise ValueError(f'Invalid Latitude or Longitude, got (Latitude:\'{lat}\', Longitude:\'{lng}\')')


def get_str_address(address):
    return \
        get_ob_value_primitive(address, 'AddrLine1', throw_exception=False, exception_return_value='') + ' ' + \
        get_ob_value_primitive(address, 'AddrLine2', throw_exception=False, exception_return_value='') + ' ' + \
        get_ob_value_primitive(address, 'AddrLine3', throw_exception=False, exception_return_value='') + ', ' + \
        get_ob_value_primitive(address, 'City', throw_exception=False, exception_return_value='') + ' ' + \
        get_ob_value_primitive(address, 'County', throw_exception=False, exception_return_value='') + ' ' + \
        get_ob_value_primitive(address, 'StateProvince', throw_exception=False, exception_return_value='') + ' ' + \
        get_ob_value_primitive(address, 'ZipPostalCode', throw_exception=False, exception_return_value='')


def get_location_gecode_address_str(address):
    """
    Returns the latlng of an address given in the request Address parameter
    The format is an Orange Button Location object: https://obeditor.sunspec.org/#/?views=Location
    """
    location = {
        'Latitude': {
            'Value': None
        },
        'Longitude': {
            'Value': None
        }
    }
    geo_res = []
    if address is not None:
        geo_res = gmaps.geocode(address)
    if len(geo_res) != 0:
        latitude = geo_res[0]['geometry']['location']['lat']
        longitude = geo_res[0]['geometry']['location']['lng']
        location['Latitude']['Value'] = latitude
        location['Longitude']['Value'] = longitude
    return location


def simple_sanitize(s: str):
    """
    Sanitize SQL string inputs simply by dropping ';' and '''
    """
    return s.replace(';', '').replace('\'', '')


def get_name_query_cond(type: str, val: str, query_params: dict):
    """
    Returns the entered string as part of an SQL
    condition on the AHJ table of the form:
            AHJ.`type` = 'val' AND
    if val is not None, otherwise it returns the
    empty string to represent no condition on type.
    """
    if val is not None:
        query_params[type] = '%' + val + '%'
        return 'AHJ.' + type + ' LIKE %(' + type + ')s AND '
    return ''


def get_list_query_cond(type: str, val: str, query_params: dict):
    """
    Returns the entered list of strings as part of
    an SQL condition on the AHJ table of the form:
            (AHJ.`type` = 'val1' OR AHJ.`type` = 'val2' OR ... ) AND
    """
    if val is not None:
        or_list = []
        for i in range(len(val)):
            param_name = f'{type}{i}'
            query_params[param_name] = val[i]
            or_list.append('AHJ.' + type + '=%(' + param_name + ')s')
        ret_str = '(' + ' OR '.join(or_list) + ') AND '
        return ret_str
    return ''


def get_basic_user_query_cond(type: str, val: str, query_params: dict):
    if val is not None:
        query_params[type] = val
        return 'Address.' + type + '=%(' + type + ')s AND '
    return ''


def get_basic_query_cond(type: str, val: str, query_params: dict):
    """
    Returns the entered string as part of an SQL
    condition on the AHJ table of the form:
            AHJ.`type` = 'val' AND
    if val is not None, otherwise it returns the
    empty string to represent no condition on type.
    """
    if val is not None:
        query_params[type] = val
        return 'AHJ.' + type + '=%(' + type + ')s AND '
    return ''


def point_to_polygon_geojson(g):
    """
    Takes a GeoJSON point and converts it
    into a GeoJSON polygon
    GeoJSON polygons must have 0 or >= 4 points
    so the GeoJSON point coordinates are duplicated 4 times
    """
    point_coordinates = g['geometry']['coordinates']
    polygon_geojson = {
        'type': 'Feature',
        'properties': g['properties'],
        'geometry': {
            'type': 'Polygon',
            'coordinates': [
                [point_coordinates, point_coordinates, point_coordinates, point_coordinates]
            ]
        }
    }
    return polygon_geojson


def get_multipolygon(request, location):
    """
    Takes a http POST request and checks if it has a FeatureCollection field.
    FeatureCollection field is expected to be GeoJSON.
    Returns None if FeatureCollection not found.
    Returns given GeoJSON into a MultiPolygon in WKT form.
    """
    geometries = request.data.get('FeatureCollection', None)
    if geometries is not None:
        geometry_list = []
        for g in geometries['features']:
            if g['geometry']['type'] == 'Point':
                g = point_to_polygon_geojson(g)
            geometry_list.append(GEOSGeometry(json.dumps(g['geometry'])))
        lng, lat = location['Longitude']['Value'], location['Latitude']['Value']
        if lat is not None and lng is not None:
            loc_point = {'type': 'Feature', 'properties': {}, 'geometry': {'type': 'Point', 'coordinates': [lng, lat]}}
            loc_polygon = point_to_polygon_geojson(loc_point)
            geometry_list.append(GEOSGeometry(json.dumps(loc_polygon['geometry'])))
        return MultiPolygon(geometry_list)
    return None


def get_multipolygon_wkt(multipolygon):
    return multipolygon.wkt.replace(" ", "", 1)


def filter_ahjs(AHJName=None, AHJID=None, AHJPK=None, AHJCode=None, AHJLevelCode=None,
                BuildingCode=None, ElectricCode=None, FireCode=None, ResidentialCode=None, WindCode=None,
                StateProvince=None, location=None, polygon=None):
    """
    Main Idea: This functional view uses raw SQL queries to
    get the information out of the databases. To make this
    dynamic, we have to check which fields were passed
    in with the request params, and modify the query
    according.

    Most difficult is the Polygon modifications due to
    the polygon structure. However, we simply check the
    points from a State -> County -> City level to filter
    at each step.

    The other filtering such as BuildingCode, FireCode, ...
    are simply expanded as where clauses on the final
    condition. AHJName is a slight exception to this as
    we match any names that contain the string that was
    given (case insensitive). Lastly, the StateProvince
    also requires extra logic because it will modify the
    query to also join on the Address table.
    """

    full_query_string = ''' SELECT * FROM AHJ '''
    query_params = {}

    if location is not None or polygon is not None:
        if polygon is not None:
            intersects = 'ST_INTERSECTS(Polygon, ST_GeomFromText(\'' + polygon + '\'))'
        else:
            intersects = 'ST_CONTAINS(Polygon, ' + location + ')'

        # State IDS that contain the location
        state_ids = ''' 
             (SELECT Polygon.PolygonID FROM Polygon 
             JOIN StatePolygon 
             on Polygon.PolygonID = StatePolygon.PolygonID 
             WHERE ''' + intersects + ')'

        # All polygon ids that contain the location
        polygonset = '''
             (SELECT PolygonID FROM StatePolygon
             WHERE PolygonID IN ''' + state_ids + \
                     ''' UNION
             SELECT Polygon.PolygonID FROM Polygon
             JOIN CountyPolygon
             on Polygon.PolygonID = CountyPolygon.PolygonID
             WHERE
             CountyPolygon.StatePolygonID IN ''' + state_ids + \
                     '''AND ''' + intersects + \
                     ''' UNION
             SELECT Polygon.PolygonID FROM Polygon
             JOIN CityPolygon
             on Polygon.PolygonID = CityPolygon.PolygonID
             WHERE
             CityPolygon.StatePolygonID IN ''' + state_ids + \
                     ' AND ' + intersects + \
                     ''' UNION
             SELECT Polygon.PolygonID FROM Polygon
             JOIN CityPolygon
             on Polygon.PolygonID = CityPolygon.PolygonID
             WHERE
             CityPolygon.StatePolygonID IN ''' + state_ids + \
                ' AND ' + intersects + \
                    ''' UNION
            SELECT Polygon.PolygonID FROM Polygon
            JOIN CountySubdivisionPolygon
            on Polygon.PolygonID = CountySubdivisionPolygon.PolygonID
            WHERE
            CountySubdivisionPolygon.StatePolygonID IN ''' + state_ids + \
                ' AND ' + intersects + ')'

        # Join AHJ on SUBQPOLYS (temp relation containing matching PolygonID)
        polygon_query = '''
            SELECT * FROM AHJ join ''' + polygonset + '''
            AS SUBQPOLYS ON AHJ.PolygonID = SUBQPOLYS.PolygonID
            '''
        # Change the stem of the query string
        full_query_string = polygon_query

    # Initialize empty where clause filtering
    where_clauses = ''
    # NOTE: StateProvince is located in the Address table,
    # so the StateProvince query needs to join a table and
    # include a where condition
    _state = StateProvince
    if _state is not None:
        query_params['StateProvince'] = _state
        full_query_string += ' JOIN Address ON AHJ.AddressID = Address.AddressID '
        where_clauses += ' Address.StateProvince=%(StateProvince)s AND '

    # Match a partially matching string for name
    where_clauses += get_name_query_cond('AHJName', AHJName, query_params)

    # Append additional clauses onto condition when NOT NULL, (checked by `basic_query_cond`
    where_clauses += get_basic_query_cond('AHJPK', AHJPK, query_params)
    where_clauses += get_basic_query_cond('AHJID', AHJID, query_params)
    where_clauses += get_basic_query_cond('AHJPK', AHJPK, query_params)
    where_clauses += get_basic_query_cond('AHJCode', AHJCode, query_params)
    where_clauses += get_basic_query_cond('AHJLevelCode', AHJLevelCode, query_params)
    where_clauses += get_list_query_cond('BuildingCode', BuildingCode, query_params)
    where_clauses += get_list_query_cond('ElectricCode', ElectricCode, query_params)
    where_clauses += get_list_query_cond('FireCode', FireCode, query_params)
    where_clauses += get_list_query_cond('ResidentialCode', ResidentialCode, query_params)
    where_clauses += get_list_query_cond('WindCode', WindCode, query_params)
    # NOTE: we append a 'True' at the end to always make the query valid
    # because the get_x_query_cond appends an `AND` to the condition
    full_query_string += ' WHERE ' + where_clauses + ' True;'
    # print(AHJ.objects.raw('EXPLAIN ' + full_query_string, query_params))
    return AHJ.objects.raw(full_query_string, query_params)


def filter_users(request):
    """
    Main Idea: This functional view uses raw SQL queries to
    get the information out of the databaes. To make this
    dynamic, we have to check which fields were passed
    in with the request params, and modify the query
    according.
    """
    # Initialize empty where clause filtering
    where_clauses = ''
    search_option = 'User.'

    where_clauses += get_basic_user_query_cond('Country',
        request.GET.get('Country[]', None))
    where_clauses += get_basic_user_query_cond('StateProvince',
        request.GET.get('StateProvince', None))
    
    search_option += request.GET.get('SearchOption', None)
    where_clauses = simple_sanitize(where_clauses)
    search_option = simple_sanitize(search_option)

    full_query_string = ''' SELECT User.UserID, User.Username, 
                                   User.Photo, User.SignupDate, 
                                   User.CommunityScore
                            FROM User 
                            WHERE User.ContactID IN (
                                SELECT Contact.ContactID 
                                FROM Contact 
                                WHERE Contact.AddressID IN (
                                    SELECT Address.AddressID 
                                    FROM Address 
                                    WHERE ''' + where_clauses + ''' True) 
                                )
                                ORDER BY '''+ search_option +  ''' DESC;'''

    return User.objects.raw(full_query_string)


def order_ahj_list_AHJLevelCode_PolygonLandArea(ahj_list):
    ahj_list.sort(key=lambda ahj: int(ahj.PolygonID.LandArea) if ahj.PolygonID is not None else 0) # Sort first by landarea ascending
    ahj_list.sort(reverse=True, key=lambda ahj: int(ahj.AHJLevelCode) if ahj.AHJLevelCode != '' else 0) # Then sort by numerical value AHJLevelCode descending
    return ahj_list


def get_public_api_serializer_context():
    context = {'is_public_view': True}
    return context


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
