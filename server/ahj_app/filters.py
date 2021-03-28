from django_filters import rest_framework as d_filters
import googlemaps
from django.contrib.gis.geos import Point
from .models import *

from django.db.models.query import QuerySet


gmaps = googlemaps.Client(key='AIzaSyAg3__F_wwwGs128CvNEdgsuRafkm1BIE4')

"""
Custom filter method to filter by latlng
Extends BaseInFilter so it can be used with a django-filter FilterSet
"""
class LocationFilter(d_filters.BaseInFilter):
    def filter(self, qs: 'QuerySet[AHJ]', value: str) -> 'QuerySet[AHJ]':
        if value is None or len(value) != 2:
            return qs
        try:
            latitude = float(value[0])
            longitude = float(value[1])
            point = Point(longitude, latitude)
            polys = Polygon.objects.filter(mpoly__intersects=point)
            return qs.filter(mpoly__in=polys)
        except ValueError:
            return qs

"""
This adds GET request parameter keys that users can filter AHJs by
It looks for the given field on the model used in the class based view that
this filter is used in.
django-filter FilterSet: https://django-filter.readthedocs.io/en/stable/guide/rest_framework.html
"""
class AHJFilter(d_filters.FilterSet):
    AHJID = d_filters.UUIDFilter(field_name='AHJID', lookup_expr='exact')
    AHJName = d_filters.CharFilter(field_name='AHJName', lookup_expr='icontains')
    AHJCode = d_filters.CharFilter(field_name='AHJCode', lookup_expr='exact')
    BuildingCode = d_filters.CharFilter(field_name='BuildingCode', lookup_expr='exact')
    ElectricCode = d_filters.CharFilter(field_name='ElectricCode', lookup_expr='exact')
    ResidentialCode = d_filters.CharFilter(field_name='ResidentialCode', lookup_expr='exact')
    FireCode = d_filters.CharFilter(field_name='FireCode', lookup_expr='exact')
    Location = LocationFilter()
