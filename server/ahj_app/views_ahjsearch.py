import csv
import json

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .models import AHJ
from .serializers import AHJSerializer
from .utils import get_multipolygon, get_multipolygon_wkt, get_str_location, \
    filter_ahjs, order_ahj_list_AHJLevelCode_PolygonLandArea, get_location_gecode_address_str, dict_to_flattened_dict_rows


@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def webpage_ahj_list(request):
    """
    Functional view for the WebPageAHJList
    """
    # By default select all the AHJs
    # filter by the latitude, longitude
    json_location = get_location_gecode_address_str(request.data.get('Address', None))

    polygon = get_multipolygon(request=request, location=json_location)
    polygon_wkt = None
    if polygon is not None:
        polygon_wkt = get_multipolygon_wkt(multipolygon=polygon)
    str_location = get_str_location(location=json_location)

    ahjs = filter_ahjs(
        AHJName=request.data.get('AHJName', None),
        AHJID=request.data.get('AHJID', None),
        AHJPK=request.data.get('AHJPK', None),
        AHJCode=request.data.get('AHJCode', None),
        AHJLevelCode=request.data.get('AHJLevelCode', None),
        BuildingCode=request.data.get('BuildingCode', []),
        ElectricCode=request.data.get('ElectricCode', []),
        FireCode=request.data.get('FireCode', []),
        ResidentialCode=request.data.get('ResidentialCode', []),
        WindCode=request.data.get('WindCode', []),
        StateProvince=request.data.get('StateProvince', None),
        location=str_location, polygon=polygon_wkt)

    if polygon is not None and str_location is None:
        """
        If a polygon was searched, and a location was not,
        set the Location object returned to represent the center of the polygon.
        """
        polygon_center = polygon.centroid
        json_location = {'Latitude': {'Value': polygon_center[1]}, 'Longitude': {'Value': polygon_center[0]}}

    serializer = AHJSerializer
    paginator = LimitOffsetPagination()
    context = {'is_public_view': request.data.get('use_public_view', False)}
    page = paginator.paginate_queryset(ahjs, request)

    if str_location is not None or polygon is not None:
        """
        Sort the AHJs returned if a location or polygon was searched
        """
        page = order_ahj_list_AHJLevelCode_PolygonLandArea(page)

    payload = serializer(page, many=True, context=context).data

    if request.data.get('return_attachment', False):
        return get_file_response(serializer(ahjs, many=True, context={'is_public_view': True}).data, content_type=request.data.get('file_type', 'application/json'))
    else:
        return paginator.get_paginated_response({
            'Location': json_location,
            'ahjlist': payload
        })


@api_view(['GET'])
def get_single_ahj(request):
    """
    Endpoint to get a single ahj given an AHJPK
    """
    try:
        ahj = AHJ.objects.get(AHJPK=request.query_params.get('AHJPK'))
        return Response(AHJSerializer(ahj).data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


def write_response_csv_dict_writer(obj_list):
    """
    Creates an HTTP response with CSV data written by csv.DictWriter.
    """
    column_names = obj_list[0].keys()
    column_dict = {k: k for k in obj_list[0].keys()}
    response = HttpResponse(content_type='text/csv')
    writer = csv.DictWriter(response, fieldnames=column_names)
    writer.writerow(column_dict)
    for o in obj_list:
        writer.writerow(o)
    return response


def write_response_json(obj):
    """
    Creates an HTTP response with JSON data written.
    """
    return HttpResponse(json.dumps(obj), content_type='application/json')


def make_file_response(http_response, filename=f'ahj_registry_download', file_ext='.txt'):
    """
    Takes an HTTP response and sets it as a file attachment.
    """
    http_response['Content-Disposition'] = f'attachment; filename={filename}{file_ext}'
    return http_response


def get_file_response(data, content_type=''):
    """
    Returns an HTTP response of a file attachment with the given data written to it.
    """
    if content_type == 'text/csv':
        return make_file_response(write_response_csv_dict_writer(dict_to_flattened_dict_rows(data)), file_ext='.csv')
    elif content_type == 'application/json':
        return make_file_response(write_response_json(data), file_ext='.json')
    else:
        return Response('Unknown file type', status=status.HTTP_400_BAD_REQUEST)
