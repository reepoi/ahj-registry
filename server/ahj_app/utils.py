import json
import re

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.utils.serializer_helpers import ReturnDict

from .serializers import *
import googlemaps
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon


ENUM_FIELDS = {
    'BuildingCode',
    'ElectricCode',
    'FireCode',
    'ResidentialCode',
    'WindCode',
    'AHJLevelCode',
    'DocumentSubmissionMethod',
    'PermitIssueMethod',
    'AddressType',
    'LocationDeterminationMethod',
    'LocationType',
    'ContactType',
    'PreferredContactMethod',
    'EngineeringReviewType',
    'RequirementLevel',
    'StampType',
    'FeeStructureType',
    'InspectionType'
}

ENUM_PLURALS_TRANSLATE = {
    'DocumentSubmissionMethods': 'DocumentSubmissionMethod',
    'PermitIssueMethods': 'PermitIssueMethod'
}


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
        if throw_exception and field_name in ob_json: # Throws exception if the json had the key but it was not in correct OB format
            raise ValueError(f'Missing \'Value\' key for Orange Button field \'{field_name}\'')
        return exception_return_value # returns empty string if the json didn't have the field name as a key

def check_address_empty(address):
    return re.search('[a-zA-Z0-9]', address) # If number or letter exists, then at least one address field has been provided


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
        get_ob_value_primitive(address, 'AddrLine1', exception_return_value='') + ' ' + \
        get_ob_value_primitive(address, 'AddrLine2', exception_return_value='') + ' ' + \
        get_ob_value_primitive(address, 'AddrLine3', exception_return_value='') + ', ' + \
        get_ob_value_primitive(address, 'City', exception_return_value='') + ' ' + \
        get_ob_value_primitive(address, 'County', exception_return_value='') + ' ' + \
        get_ob_value_primitive(address, 'StateProvince', exception_return_value='') + ' ' + \
        get_ob_value_primitive(address, 'ZipPostalCode', exception_return_value='')


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
    if bool(address): # Check if address is non-falsey
        geo_res = gmaps.geocode(address)
    if len(geo_res) != 0:
        latitude = geo_res[0]['geometry']['location']['lat']
        longitude = geo_res[0]['geometry']['location']['lng']
        location['Latitude']['Value'] = latitude
        location['Longitude']['Value'] = longitude
    return location

def get_elevation(Address):
    loc = get_location_gecode_address_str(Address)
    location = { 'lat': loc['Latitude']['Value'], 'lng': loc['Longitude']['Value'] }
    elev = gmaps.elevation((loc['Latitude']['Value'],loc['Longitude']['Value']))
    loc['Elevation'] = {'Value': 0}
    loc['Elevation']['Value'] = elev[0]['elevation']
    return loc

def get_enum_value_row(enum_field, enum_value):
    """
    Finds the row of the enum table given the field name and its enum value.
    """
    # Translate plural, if given
    enum_field = ENUM_PLURALS_TRANSLATE[enum_field] if enum_field in ENUM_PLURALS_TRANSLATE else enum_field
    return apps.get_model('ahj_app', enum_field).objects.get(Value=enum_value)


def get_enum_value_row_else_null(enum_field, enum_value):
    try:
        if enum_value is None:
            return None
        elif isinstance(enum_value, list):
            return [get_enum_value_row_else_null(enum_field, v) for v in enum_value]
        return get_enum_value_row(enum_field, enum_value)
    except ObjectDoesNotExist:
        return None


def simple_sanitize(s: str):
    """
    Sanitize SQL string inputs simply by dropping ';' and '''
    """
    if s is not None:
        return s.replace(';', '').replace('\'', '')
    return None


def get_name_query_cond(type: str, val: str, query_params: dict):
    """
    Returns the entered string as part of an SQL
    condition on the AHJ table of the form:
            AHJ.`type` = 'val' AND
    if val is not None, otherwise it returns the
    empty string to represent no condition on type.
    """
    if val is not None and type is not None:
        query_params[type] = '%' + val + '%'
        return 'AHJ.' + type + ' LIKE %(' + type + ')s AND '
    return ''


def get_list_query_cond(type: str, val: list, query_params: dict):
    """
    Returns the entered list of strings as part of
    an SQL condition on the AHJ table of the form:
            (AHJ.`type` = 'val1' OR AHJ.`type` = 'val2' OR ... ) AND
    """
    if val is not None and len(val) != 0:
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
                BuildingCode=[], ElectricCode=[], FireCode=[], ResidentialCode=[], WindCode=[],
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
    where_clauses += get_basic_query_cond('AHJLevelCode', getattr(get_enum_value_row_else_null('AHJLevelCode', AHJLevelCode), 'pk', None), query_params)
    where_clauses += get_list_query_cond('BuildingCode', [e.pk for e in get_enum_value_row_else_null('BuildingCode', BuildingCode) if e is not None], query_params)
    where_clauses += get_list_query_cond('ElectricCode', [e.pk for e in get_enum_value_row_else_null('ElectricCode', ElectricCode) if e is not None], query_params)
    where_clauses += get_list_query_cond('FireCode', [e.pk for e in get_enum_value_row_else_null('FireCode', FireCode) if e is not None], query_params)
    where_clauses += get_list_query_cond('ResidentialCode', [e.pk for e in get_enum_value_row_else_null('ResidentialCode', ResidentialCode) if e is not None], query_params)
    where_clauses += get_list_query_cond('WindCode', [e.pk for e in get_enum_value_row_else_null('WindCode', WindCode) if e is not None], query_params)

    # NOTE: we append a 'True' at the end to always make the query valid
    # because the get_x_query_cond appends an `AND` to the condition
    full_query_string += ' WHERE ' + where_clauses + ' True;'
    #print(AHJ.objects.raw('EXPLAIN ' + full_query_string, query_params))
    return AHJ.objects.raw(full_query_string, query_params)

def order_ahj_list_AHJLevelCode_PolygonLandArea(ahj_list):
    ahj_list.sort(key=lambda ahj: int(ahj.PolygonID.LandArea) if ahj.PolygonID is not None else 0) # Sort first by landarea ascending
    ahj_list.sort(reverse=True, key=lambda ahj: int(ahj.AHJLevelCode.Value) if ahj.AHJLevelCode != '' and ahj.AHJLevelCode is not None else 0) # Then sort by numerical value AHJLevelCode descending
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


def filter_dict_keys(dict_to_filter, keys_to_keep):
    return {k: v for k, v in dict_to_filter.items() if k in keys_to_keep}


def get_model_field_names(model):
    return {field.name for field in model._meta.get_fields()}


def filter_dict_model_fields(dict_to_filter, model):
    return filter_dict_keys(dict_to_filter, get_model_field_names(model))


def flatten_dict(obj):
    result = {}

    def recurse(cur, prop):
        if type(cur) is dict or type(cur) is OrderedDict or type(cur) is ReturnDict:
            is_empty = True
            for p in cur.keys():
                is_empty = False
                recurse(cur[p], f'{prop}.{p}' if prop != '' else p)
            if is_empty and prop != '':
                result[prop] = {}
        elif type(cur) is list:
            cur_len = len(cur)
            for x in range(cur_len):
                recurse(cur[x], f'{prop}[{x}]')
            if cur_len == 0:
                result[prop] = []
        else:
            result[prop] = cur

    recurse(obj, '')
    return result


def split_flattened_dict_keys(key):
    """
    Splits flattened json keys into the individual dict keys.
    For example, Contacts[0].FirstName.Value -> [Contacts, 0, FirstName, Value]
    """
    return [k for k in re.split(r'[.[\]]', key) if k != '']


def index_dict_flattened_dict_key(obj, key, no_exception=False, key_error_default=''):
    try:
        result = obj
        keys = split_flattened_dict_keys(key)
        for k in keys:
            result = result[k if not k.isnumeric() else int(k)]
        return result
    except KeyError as e:
        if no_exception:
            return key_error_default
        raise e


def dict_to_csv_dict_rows(obj):
    flattened_obj = flatten_dict(obj)
    # Keep only Orange Button primitive values
    obj_keys = flattened_obj.keys()
    csv_rows = []
    if type(obj) is list:
        # Remove '[#].' prefix of keys
        obj_keys = {k[k.index('.') + 1:] for k in obj_keys}
        for o in obj:
            row = {k: index_dict_flattened_dict_key(o, k, no_exception=True) for k in obj_keys}
            csv_rows.append(row)
    else:
        row = {k: index_dict_flattened_dict_key(obj, k) for k in obj_keys}
        csv_rows.append(row)
    return csv_rows


def filter_dict_keys_orange_button_primitives(obj):
    return {k: v for k, v in obj.items() if k.endswith(('Value', 'Decimals', 'Precision',
                                                        'StartTime', 'EndTime', 'Unit'))}
