from rest_framework import status
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .authentication import WebpageTokenAuth
from .models import AHJ
from .serializers import AHJSerializer
from .utils import get_location, get_multipolygon, get_multipolygon_wkt, get_str_location, \
    filter_ahjs, order_ahj_list_AHJLevelCode_PolygonLandArea


@api_view(['POST'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def webpage_ahj_list(request):
    """
    Functional view for the WebPageAHJList
    """
    # By default select all the AHJs
    # filter by the latitude, longitude
    json_location = get_location(request=request)
    polygon = get_multipolygon(request=request, location=json_location)
    polygon_wkt = None
    if polygon is not None:
        polygon_wkt = get_multipolygon_wkt(multipolygon=polygon)
    str_location = get_str_location(location=json_location)
    ahjs = filter_ahjs(request, str_location, polygon_wkt)
    if polygon is not None and str_location is None:
        polygon_center = polygon.centroid
        json_location = {'Latitude': {'Value': polygon_center[1]}, 'Longitude': {'Value': polygon_center[0]}}
    serializer = AHJSerializer
    paginator = LimitOffsetPagination()
    context = {'fields_to_drop': []}
    page = paginator.paginate_queryset(ahjs, request)
    if str_location is not None:
        page = order_ahj_list_AHJLevelCode_PolygonLandArea(page)
    try:
        payload = serializer(page, many=True, context=context).data
    except Exception as e:
        print(e)

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
