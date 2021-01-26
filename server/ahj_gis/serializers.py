from rest_framework_gis import serializers as geo_serializers
from rest_framework import serializers
from .models import Polygon
from core.models import AHJ


class FindPolygonAHJID(serializers.UUIDField):
    def to_representation(self, value):
        # Some polygons have multiple AHJ paired with them
        # This is because there are duplicate AHJ (data issue)
        ahj = AHJ.objects.filter(mpoly=value).first()
        if ahj is None:
            return None
        else:
            return ahj.AHJID


class PolygonSerializer(geo_serializers.GeoFeatureModelSerializer):
    AHJID = FindPolygonAHJID(source='*')
    class Meta:
        model = Polygon
        geo_field = 'mpoly'
        id_field = False
        fields = ['AHJID', 'ALAND', 'INTPTLAT', 'INTPTLON', 'GEOID']
