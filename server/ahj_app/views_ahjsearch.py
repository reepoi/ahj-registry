from rest_framework import status
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .authentication import WebpageTokenAuth
from .models import AHJ
from .serializers import AHJSerializer
from .utils import get_multipolygon, get_multipolygon_wkt, get_str_location, \
    filter_ahjs, order_ahj_list_AHJLevelCode_PolygonLandArea, get_location_gecode_address_str


@api_view(['POST'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
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
    context = {'fields_to_drop': []}
    page = paginator.paginate_queryset(ahjs, request)

    if str_location is not None or polygon is not None:
        """
        Sort the AHJs returned if a location or polygon was searched
        """
        page = order_ahj_list_AHJLevelCode_PolygonLandArea(page)

    payload = serializer(page, many=True, context=context).data

    return paginator.get_paginated_response({
        'Location': json_location,
        'ahjlist': payload
    })


@api_view(['GET'])
def get_single_ahj(request):
    AHJPK = request.GET.get('AHJPK')
    ahj = AHJ.objects.filter(AHJPK=AHJPK)
    context = {'fields_to_drop': []}
    return Response(AHJSerializer(ahj, context=context, many=True).data, status=status.HTTP_200_OK)
