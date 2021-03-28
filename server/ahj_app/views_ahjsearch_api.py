from rest_framework import status
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .authentication import APITokenAuth
from .serializers import AHJSerializer
from .utils import order_ahj_list_AHJLevelCode_PolygonLandArea, filter_ahjs, get_str_location, \
    get_location, get_public_api_serializer_context, get_multipolygon_wkt, get_multipolygon


def get_ob_value_primitive(field):
    if isinstance(field, dict) and 'Value' in field:
        return field['Value']
    return ''


@api_view(['POST'])
@authentication_classes([APITokenAuth])
@permission_classes([IsAuthenticated])
def ahj_list(request):
    """
    Functional view for the AHJList
    """
    # TODO move authentication to a separate function
    # By default select all the AHJs
    # filter by the latitude, longitude
    json_location = get_location(request=request)
    polygon = get_multipolygon(request=request, location=json_location)
    polygon_wkt = None
    if polygon is not None:
        polygon_wkt = get_multipolygon_wkt(multipolygon=polygon)
    str_location = get_str_location(location=json_location)
    ahjs = filter_ahjs(request, str_location, polygon_wkt)
    serializer = AHJSerializer
    paginator = LimitOffsetPagination()
    context = get_public_api_serializer_context()
    page = paginator.paginate_queryset(ahjs, request)
    if str_location is not None:
        page = order_ahj_list_AHJLevelCode_PolygonLandArea(page)
    payload = serializer(page, many=True, context=context).data
    return paginator.get_paginated_response(payload)


@api_view(['POST'])
@authentication_classes([APITokenAuth])
@permission_classes([IsAuthenticated])
def ahj_geo_location(request):
    ahjs_to_search = request.data.get('ahjs_to_search', None)

    # If sent an Orange Button Address
    ob_location = request.data.get('Location', None)
    if ob_location is None:
        # If sent an Orange Button Location
        ob_location = request.data
    try:
        latitude = get_ob_value_primitive(ob_location.get('Latitude', None))
        longitude = get_ob_value_primitive(ob_location.get('Longitude', None))
        float(latitude)
        float(longitude)
    except (TypeError, KeyError, ValueError):
        return Response('Missing or invalid Orange Button Latitude or Longitude values',
                        status=status.HTTP_400_BAD_REQUEST)
    str_location = get_str_location(ob_location)

    # Other filters aren't allowed on this endpoint
    request.data.clear()
    ahjs = filter_ahjs(request, location=str_location, polygon=None)

    # Only include ahjs whose AHJID is in ahjs_to_search, if ahjs_to_search was given
    if ahjs_to_search is None:
        ahj_result = [ahj for ahj in ahjs]
    else:
        ahj_result = [ahj for ahj in ahjs if ahj.AHJID in ahjs_to_search]
    ahj_result = order_ahj_list_AHJLevelCode_PolygonLandArea(ahj_result)
    return Response(AHJSerializer(ahj_result, many=True, context=get_public_api_serializer_context()).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([APITokenAuth])
@permission_classes([IsAuthenticated])
def ahj_geo_address(request):
    ob_address = request.data
    ahjs_to_search = request.data.get('ahjs_to_search', None)
    addrline1 = get_ob_value_primitive(ob_address.get('AddrLine1', ''))
    addrline2 = get_ob_value_primitive(ob_address.get('AddrLine2', ''))
    addrline3 = get_ob_value_primitive(ob_address.get('AddrLine3', ''))
    city = get_ob_value_primitive(ob_address.get('City', ''))
    county = get_ob_value_primitive(ob_address.get('County', ''))
    state_province = get_ob_value_primitive(ob_address.get('StateProvince', ''))
    zip_postal_code = get_ob_value_primitive(ob_address.get('ZipPostalCode', ''))
    address = addrline1 + ' ' + addrline2 + ' ' + addrline3 + ', ' + city + ' ' + county + ' ' + state_province + ' ' + zip_postal_code
    request.data.clear()
    request.data.update({'Address': address})
    ob_location = get_location(request)
    str_location = get_str_location(ob_location)

    # Other filters aren't allowed on this endpoint
    request.data.clear()
    ahjs = filter_ahjs(request, location=str_location, polygon=None)

    # Only include ahjs whose AHJID is in ahjs_to_search, if ahjs_to_search was given
    if ahjs_to_search is None:
        ahj_result = [ahj for ahj in ahjs]
    else:
        ahj_result = [ahj for ahj in ahjs if ahj.AHJID in ahjs_to_search]
    ahj_result = order_ahj_list_AHJLevelCode_PolygonLandArea(ahj_result)
    return Response(AHJSerializer(ahj_result, many=True, context=get_public_api_serializer_context()).data, status=status.HTTP_200_OK)