from rest_framework.utils import json
from .utils import filter_ahjs_by_location, get_orange_button_value_primitive
from rest_framework.decorators import api_view
from core.models import AHJ
from core.serializers import AHJSerializer
from rest_framework.response import Response
from .constants import GOOGLE_GEOCODING_API_KEY
from googlemaps import Client
from rest_framework import status
from core.utils import set_view_mode

gmaps = Client(key=GOOGLE_GEOCODING_API_KEY)


@api_view(['POST'])
def find_ahj_location(request):
    if request.auth is None:
        return Response({'detail': 'No authentication provided'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.data.get('Location') is None:
        # The data is an Location
        location = request.data
    else:
        # The data is a Address
        location = request.data.get('Location')

    longitude = get_orange_button_value_primitive(location.get('Longitude', ''))
    latitude = get_orange_button_value_primitive(location.get('Latitude', ''))

    try:
        longitude = float(longitude)
        latitude = float(latitude)
    except (TypeError, ValueError):
        return Response({'detail': 'invalid location'}, status=status.HTTP_400_BAD_REQUEST)

    ahj_set = filter_ahjs_by_location(longitude, latitude,
                                      ahjs_to_search=request.data.get('ahjs_to_search'))

    return Response(AHJSerializer(ahj_set, many=True, context=set_view_mode(request, hide_ui_fields=True, called_by_view=True)).data, status=status.HTTP_200_OK)


@api_view(['POST'])
def find_ahj_address(request):
    if request.auth is None:
        return Response({'detail': 'No authentication provided'}, status=status.HTTP_401_UNAUTHORIZED)

    addr_line_1 = get_orange_button_value_primitive(request.data.get('AddrLine1', ''))
    addr_line_2 = get_orange_button_value_primitive(request.data.get('AddrLine2', ''))
    addr_line_3 = get_orange_button_value_primitive(request.data.get('AddrLine3', ''))
    city = get_orange_button_value_primitive(request.data.get('City', ''))
    state_province = get_orange_button_value_primitive(request.data.get('StateProvince', ''))
    zip_postal_code = get_orange_button_value_primitive(request.data.get('ZipPostalCode', ''))

    geocode_result = gmaps.geocode(addr_line_1 + ' ' + addr_line_2 + ' ' + addr_line_3 + ', ' + city + ', ' + state_province + ' ' + zip_postal_code)
    if len(geocode_result) == 0:
        return Response({'detail': 'Google Maps Geocoding failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # Find AHJ's for all possible address matches
    ahj_set = AHJ.objects.none()
    for x in range(len(geocode_result)):
        coordinates = geocode_result[x]['geometry']['location']
        longitude = coordinates['lng']
        latitude = coordinates['lat']
        ahj_set |= filter_ahjs_by_location(longitude, latitude,
                                           ahjs_to_search=request.data.get('ahjs_to_search'))

    return Response(AHJSerializer(ahj_set, many=True, context=set_view_mode(request, hide_ui_fields=True, called_by_view=True)).data, status=status.HTTP_200_OK)
