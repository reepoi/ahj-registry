from django.db import connection
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .authentication import WebpageTokenAuth
from .models import Polygon
from .serializers import DataVisAHJPolygonInfoSerializer, PolygonSerializer
from .utils import simple_sanitize, dictfetchall


@api_view(['GET'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def data_map(request):
    """
    View to return statistics about ahjs across the country
    If given a StatePK, returns stats for each ahj in the state
    else gives overall stats for every state
    """
    statepolygon_pk = request.query_params.get('StatePK', None)
    polygon_columns = 'Name, Polygon.PolygonID, InternalPLatitude, InternalPLongitude, Name'
    ahj_columns = 'AHJPK, AHJName'
    serializer_context = {}
    if statepolygon_pk is not None:
        statepolygon_pk = simple_sanitize(statepolygon_pk)
        query = 'SELECT ' + \
                polygon_columns + ', ' + ahj_columns + ', ' +\
                'if(BuildingCode!="",1,0) as numBuildingCodes,' + \
                'if(ElectricCode!="",1,0) as numElectricCodes,' + \
                'if(FireCode!="",1,0) as numFireCodes,' + \
                'if(ResidentialCode!="",1,0) as numResidentialCodes,' + \
                'if(WindCode!="",1,0) as numWindCodes' + \
                ' FROM Polygon JOIN (' \
                'SELECT PolygonID FROM CountyPolygon WHERE StatePolygonID=' + \
                statepolygon_pk + \
                ' UNION SELECT PolygonID FROM CityPolygon WHERE StatePolygonID=' + \
                statepolygon_pk + \
                ' UNION SELECT PolygonID FROM CountySubdivisionPolygon WHERE StatePolygonID=' + \
                statepolygon_pk + \
                ') as polygons_of_state ON Polygon.PolygonID=polygons_of_state.PolygonID LEFT JOIN AHJ ON Polygon.PolygonID=AHJ.PolygonID;'
    else:
        query = 'SELECT ' + polygon_columns + \
                ' FROM StatePolygon JOIN Polygon ON Polygon.PolygonID=StatePolygon.PolygonID;'
        serializer_context['is_state'] = True
    cursor = connection.cursor()
    cursor.execute(query)
    return Response(DataVisAHJPolygonInfoSerializer(dictfetchall(cursor), context=serializer_context, many=True).data)


@api_view(['GET'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def data_map_get_polygon(request):
    """
    Returns a polygon in GeoJSON given its ID
    """
    try:
        return Response(PolygonSerializer(Polygon.objects.get(PolygonID=request.query_params.get('PolygonID', None))).data)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)