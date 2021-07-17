from collections import OrderedDict

from django.db import connection
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Polygon
from .serializers import PolygonSerializer
from .utils import dictfetchall


@api_view(['GET'])
def data_map(request):
    """
    Provides data for the data coverage visualization in the client app.
    """
    try:
        state_pk = request.query_params.get('StatePK', None)
        polygon_columns = 'Polygon.PolygonID, InternalPLatitude, InternalPLongitude, Name'
        ahj_columns = 'AHJPK, AHJName'
        if state_pk is not None:
            with connection.cursor() as cursor:
                cursor.execute(f'SELECT {polygon_columns}, {ahj_columns}, '
                               'IF(BuildingCode IS NULL,0,1) as numBuildingCodes,'
                               'IF(ElectricCode IS NULL,0,1) as numElectricCodes,'
                               'IF(FireCode IS NULL,0,1) as numFireCodes,'
                               'IF(ResidentialCode IS NULL,0,1) as numResidentialCodes,'
                               'IF(WindCode IS NULL,0,1) as numWindCodes FROM '
                               '(SELECT PolygonID FROM CountyPolygon WHERE StatePolygonID=%(StatePK)s '
                               'UNION SELECT PolygonID FROM CityPolygon WHERE StatePolygonID=%(StatePK)s '
                               'UNION SELECT PolygonID FROM CountySubdivisionPolygon WHERE StatePolygonID=%(StatePK)s) '
                               'as polygons_of_state '
                               'JOIN Polygon ON Polygon.PolygonID=polygons_of_state.PolygonID '
                               'LEFT JOIN AHJ ON Polygon.PolygonID=AHJ.PolygonID;',
                               params={'StatePK': state_pk})
                results = dictfetchall(cursor)
        else:
            with connection.cursor() as cursor:
                cursor.execute('SELECT numAHJs, numBuildingCodes, numElectricCodes, numFireCodes,'
                               f'numResidentialCodes, numWindCodes, {polygon_columns} FROM '
                               '(SELECT COUNT(*) as numAHJs,'
                               'SUM(BuildingCode IS NOT NULL) as numBuildingCodes,'
                               'SUM(ElectricCode IS NOT NULL) as numElectricCodes,'
                               'SUM(FireCode IS NOT NULL) as numFireCodes,'
                               'SUM(ResidentialCode IS NOT NULL) as numResidentialCodes,'
                               'SUM(WindCode IS NOT NULL) as numWindCodes,'
                               'StatePolygonID FROM '
                               '(SELECT PolygonID, StatePolygonID FROM CountyPolygon '
                               'UNION SELECT PolygonID, StatePolygonID FROM CityPolygon '
                               'UNION SELECT PolygonID, StatePolygonID FROM CountySubdivisionPolygon) '
                               'as polygons_of_state '
                               'LEFT JOIN AHJ ON polygons_of_state.PolygonID=AHJ.PolygonID GROUP BY StatePolygonID) '
                               'as all_states '
                               'RIGHT JOIN StatePolygon ON all_states.StatePolygonID=StatePolygon.PolygonID '
                               'JOIN Polygon ON StatePolygon.PolygonID=Polygon.PolygonID;')
                results = dictfetchall(cursor)
        return Response([OrderedDict(result) for result in results], status=status.HTTP_200_OK)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def data_map_get_polygon(request):
    """
    Returns a polygon in GeoJSON given its ID
    from the request's PolygonID query parameter.
    """
    try:
        return Response(PolygonSerializer(Polygon.objects.get(PolygonID=request.query_params.get('PolygonID', None))).data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
