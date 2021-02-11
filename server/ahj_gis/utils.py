from django.contrib.gis.geos import Point
from .models import *
from core.models import AHJ, Address
import csv


def filter_ahjs_by_location(longitude, latitude, **kwargs):
    coordinate = Point(longitude, latitude)

    # Filter by intersects
    # Filter by state first
    state_set = State.objects.filter(mpoly__intersects=coordinate)

    covers_poly_set = []
    for state in state_set:
        polygon_set = Polygon.objects.filter(STATEABBR=state.STATEABBR)
        if kwargs.get('ahjs_to_search', None) is not None:
            intersects_poly_set = polygon_set.filter(ahj__AHJID__in=kwargs['ahjs_to_search']).filter(mpoly__intersects=coordinate)
        else:
            intersects_poly_set = polygon_set.filter(mpoly__intersects=coordinate)

        # Filter intersects results by covers
        for poly in intersects_poly_set:
            # Use covers to include coordinates on borders
            if poly.mpoly.covers(coordinate):
                covers_poly_set.append(poly)

    # Combine all of the AHJ's with the found names into one QuerySet
    return AHJ.objects.filter(mpoly__in=covers_poly_set).order_by('-AHJLevelCode')


def get_orange_button_value_primitive(field):
    if isinstance(field, dict) and 'Value' in field:
        return field['Value']
    return field


def add_abbr_to_state():
    states = State.objects.all()
    for poly in states:
        if poly.STATEFP == '01': poly.STATEABBR = 'AL'
        elif poly.STATEFP == '02': poly.STATEABBR = 'AK'
        elif poly.STATEFP == '60': poly.STATEABBR = 'AS'
        elif poly.STATEFP == '04': poly.STATEABBR = 'AZ'
        elif poly.STATEFP == '05': poly.STATEABBR = 'AR'
        elif poly.STATEFP == '81': poly.STATEABBR = 'BI'
        elif poly.STATEFP == '06': poly.STATEABBR = 'CA'
        elif poly.STATEFP == '08': poly.STATEABBR = 'CO'
        elif poly.STATEFP == '09': poly.STATEABBR = 'CT'
        elif poly.STATEFP == '10': poly.STATEABBR = 'DE'
        elif poly.STATEFP == '11': poly.STATEABBR = 'DC'
        elif poly.STATEFP == '12': poly.STATEABBR = 'FL'
        elif poly.STATEFP == '64': poly.STATEABBR = 'FM'
        elif poly.STATEFP == '13': poly.STATEABBR = 'GA'
        elif poly.STATEFP == '66': poly.STATEABBR = 'GU'
        elif poly.STATEFP == '15': poly.STATEABBR = 'HI'
        elif poly.STATEFP == '84': poly.STATEABBR = '84'
        elif poly.STATEFP == '16': poly.STATEABBR = 'ID'
        elif poly.STATEFP == '17': poly.STATEABBR = 'IL'
        elif poly.STATEFP == '18': poly.STATEABBR = 'IN'
        elif poly.STATEFP == '19': poly.STATEABBR = 'IA'
        elif poly.STATEFP == '86': poly.STATEABBR = 'JI'
        elif poly.STATEFP == '67': poly.STATEABBR = 'JA'
        elif poly.STATEFP == '20': poly.STATEABBR = 'KS'
        elif poly.STATEFP == '21': poly.STATEABBR = 'KY'
        elif poly.STATEFP == '89': poly.STATEABBR = 'KR'
        elif poly.STATEFP == '22': poly.STATEABBR = 'LA'
        elif poly.STATEFP == '23': poly.STATEABBR = 'ME'
        elif poly.STATEFP == '68': poly.STATEABBR = 'MH'
        elif poly.STATEFP == '24': poly.STATEABBR = 'MD'
        elif poly.STATEFP == '25': poly.STATEABBR = 'MA'
        elif poly.STATEFP == '26': poly.STATEABBR = 'MI'
        elif poly.STATEFP == '71': poly.STATEABBR = '71'
        elif poly.STATEFP == '27': poly.STATEABBR = 'MN'
        elif poly.STATEFP == '28': poly.STATEABBR = 'MS'
        elif poly.STATEFP == '29': poly.STATEABBR = 'MO'
        elif poly.STATEFP == '30': poly.STATEABBR = 'MT'
        elif poly.STATEFP == '76': poly.STATEABBR = '76'
        elif poly.STATEFP == '31': poly.STATEABBR = 'NE'
        elif poly.STATEFP == '32': poly.STATEABBR = 'NV'
        elif poly.STATEFP == '33': poly.STATEABBR = 'NH'
        elif poly.STATEFP == '34': poly.STATEABBR = 'NJ'
        elif poly.STATEFP == '35': poly.STATEABBR = 'NM'
        elif poly.STATEFP == '36': poly.STATEABBR = 'NY'
        elif poly.STATEFP == '37': poly.STATEABBR = 'NC'
        elif poly.STATEFP == '38': poly.STATEABBR = 'ND'
        elif poly.STATEFP == '69': poly.STATEABBR = 'MP'
        elif poly.STATEFP == '39': poly.STATEABBR = 'OH'
        elif poly.STATEFP == '40': poly.STATEABBR = 'OK'
        elif poly.STATEFP == '41': poly.STATEABBR = 'OR'
        elif poly.STATEFP == '70': poly.STATEABBR = 'PW'
        elif poly.STATEFP == '95': poly.STATEABBR = '95'
        elif poly.STATEFP == '42': poly.STATEABBR = 'PA'
        elif poly.STATEFP == '72': poly.STATEABBR = 'PR'
        elif poly.STATEFP == '44': poly.STATEABBR = 'RI'
        elif poly.STATEFP == '45': poly.STATEABBR = 'SC'
        elif poly.STATEFP == '46': poly.STATEABBR = 'SD'
        elif poly.STATEFP == '47': poly.STATEABBR = 'TN'
        elif poly.STATEFP == '48': poly.STATEABBR = 'TX'
        elif poly.STATEFP == '74': poly.STATEABBR = 'UM'
        elif poly.STATEFP == '49': poly.STATEABBR = 'UT'
        elif poly.STATEFP == '50': poly.STATEABBR = 'VT'
        elif poly.STATEFP == '51': poly.STATEABBR = 'VA'
        elif poly.STATEFP == '78': poly.STATEABBR = 'VI'
        elif poly.STATEFP == '79': poly.STATEABBR = '79'
        elif poly.STATEFP == '53': poly.STATEABBR = 'WA'
        elif poly.STATEFP == '54': poly.STATEABBR = 'WV'
        elif poly.STATEFP == '55': poly.STATEABBR = 'WI'
        elif poly.STATEFP == '56': poly.STATEABBR = 'WY'
        else:
            print(poly.STATEFP)
        poly.save()


def add_state_abbr():
    counties = County.objects.all()
    cities = City.objects.all()
    for poly in counties:
        if poly.STATEFP == '01': poly.STATEABBR = 'AL'
        elif poly.STATEFP == '02': poly.STATEABBR = 'AK'
        elif poly.STATEFP == '60': poly.STATEABBR = 'AS'
        elif poly.STATEFP == '04': poly.STATEABBR = 'AZ'
        elif poly.STATEFP == '05': poly.STATEABBR = 'AR'
        elif poly.STATEFP == '81': poly.STATEABBR = 'BI'
        elif poly.STATEFP == '06': poly.STATEABBR = 'CA'
        elif poly.STATEFP == '08': poly.STATEABBR = 'CO'
        elif poly.STATEFP == '09': poly.STATEABBR = 'CT'
        elif poly.STATEFP == '10': poly.STATEABBR = 'DE'
        elif poly.STATEFP == '11': poly.STATEABBR = 'DC'
        elif poly.STATEFP == '12': poly.STATEABBR = 'FL'
        elif poly.STATEFP == '64': poly.STATEABBR = 'FM'
        elif poly.STATEFP == '13': poly.STATEABBR = 'GA'
        elif poly.STATEFP == '66': poly.STATEABBR = 'GU'
        elif poly.STATEFP == '15': poly.STATEABBR = 'HI'
        elif poly.STATEFP == '84': poly.STATEABBR = '84'
        elif poly.STATEFP == '16': poly.STATEABBR = 'ID'
        elif poly.STATEFP == '17': poly.STATEABBR = 'IL'
        elif poly.STATEFP == '18': poly.STATEABBR = 'IN'
        elif poly.STATEFP == '19': poly.STATEABBR = 'IA'
        elif poly.STATEFP == '86': poly.STATEABBR = 'JI'
        elif poly.STATEFP == '67': poly.STATEABBR = 'JA'
        elif poly.STATEFP == '20': poly.STATEABBR = 'KS'
        elif poly.STATEFP == '21': poly.STATEABBR = 'KY'
        elif poly.STATEFP == '89': poly.STATEABBR = 'KR'
        elif poly.STATEFP == '22': poly.STATEABBR = 'LA'
        elif poly.STATEFP == '23': poly.STATEABBR = 'ME'
        elif poly.STATEFP == '68': poly.STATEABBR = 'MH'
        elif poly.STATEFP == '24': poly.STATEABBR = 'MD'
        elif poly.STATEFP == '25': poly.STATEABBR = 'MA'
        elif poly.STATEFP == '26': poly.STATEABBR = 'MI'
        elif poly.STATEFP == '71': poly.STATEABBR = '71'
        elif poly.STATEFP == '27': poly.STATEABBR = 'MN'
        elif poly.STATEFP == '28': poly.STATEABBR = 'MS'
        elif poly.STATEFP == '29': poly.STATEABBR = 'MO'
        elif poly.STATEFP == '30': poly.STATEABBR = 'MT'
        elif poly.STATEFP == '76': poly.STATEABBR = '76'
        elif poly.STATEFP == '31': poly.STATEABBR = 'NE'
        elif poly.STATEFP == '32': poly.STATEABBR = 'NV'
        elif poly.STATEFP == '33': poly.STATEABBR = 'NH'
        elif poly.STATEFP == '34': poly.STATEABBR = 'NJ'
        elif poly.STATEFP == '35': poly.STATEABBR = 'NM'
        elif poly.STATEFP == '36': poly.STATEABBR = 'NY'
        elif poly.STATEFP == '37': poly.STATEABBR = 'NC'
        elif poly.STATEFP == '38': poly.STATEABBR = 'ND'
        elif poly.STATEFP == '69': poly.STATEABBR = 'MP'
        elif poly.STATEFP == '39': poly.STATEABBR = 'OH'
        elif poly.STATEFP == '40': poly.STATEABBR = 'OK'
        elif poly.STATEFP == '41': poly.STATEABBR = 'OR'
        elif poly.STATEFP == '70': poly.STATEABBR = 'PW'
        elif poly.STATEFP == '95': poly.STATEABBR = '95'
        elif poly.STATEFP == '42': poly.STATEABBR = 'PA'
        elif poly.STATEFP == '72': poly.STATEABBR = 'PR'
        elif poly.STATEFP == '44': poly.STATEABBR = 'RI'
        elif poly.STATEFP == '45': poly.STATEABBR = 'SC'
        elif poly.STATEFP == '46': poly.STATEABBR = 'SD'
        elif poly.STATEFP == '47': poly.STATEABBR = 'TN'
        elif poly.STATEFP == '48': poly.STATEABBR = 'TX'
        elif poly.STATEFP == '74': poly.STATEABBR = 'UM'
        elif poly.STATEFP == '49': poly.STATEABBR = 'UT'
        elif poly.STATEFP == '50': poly.STATEABBR = 'VT'
        elif poly.STATEFP == '51': poly.STATEABBR = 'VA'
        elif poly.STATEFP == '78': poly.STATEABBR = 'VI'
        elif poly.STATEFP == '79': poly.STATEABBR = '79'
        elif poly.STATEFP == '53': poly.STATEABBR = 'WA'
        elif poly.STATEFP == '54': poly.STATEABBR = 'WV'
        elif poly.STATEFP == '55': poly.STATEABBR = 'WI'
        elif poly.STATEFP == '56': poly.STATEABBR = 'WY'
        else:
            print(poly.STATEFP)
        poly.save()
    for poly in cities:
        if poly.STATEFP == '01': poly.STATEABBR = 'AL'
        elif poly.STATEFP == '02': poly.STATEABBR = 'AK'
        elif poly.STATEFP == '60': poly.STATEABBR = 'AS'
        elif poly.STATEFP == '04': poly.STATEABBR = 'AZ'
        elif poly.STATEFP == '05': poly.STATEABBR = 'AR'
        elif poly.STATEFP == '81': poly.STATEABBR = 'BI'
        elif poly.STATEFP == '06': poly.STATEABBR = 'CA'
        elif poly.STATEFP == '08': poly.STATEABBR = 'CO'
        elif poly.STATEFP == '09': poly.STATEABBR = 'CT'
        elif poly.STATEFP == '10': poly.STATEABBR = 'DE'
        elif poly.STATEFP == '11': poly.STATEABBR = 'DC'
        elif poly.STATEFP == '12': poly.STATEABBR = 'FL'
        elif poly.STATEFP == '64': poly.STATEABBR = 'FM'
        elif poly.STATEFP == '13': poly.STATEABBR = 'GA'
        elif poly.STATEFP == '66': poly.STATEABBR = 'GU'
        elif poly.STATEFP == '15': poly.STATEABBR = 'HI'
        elif poly.STATEFP == '84': poly.STATEABBR = '84'
        elif poly.STATEFP == '16': poly.STATEABBR = 'ID'
        elif poly.STATEFP == '17': poly.STATEABBR = 'IL'
        elif poly.STATEFP == '18': poly.STATEABBR = 'IN'
        elif poly.STATEFP == '19': poly.STATEABBR = 'IA'
        elif poly.STATEFP == '86': poly.STATEABBR = 'JI'
        elif poly.STATEFP == '67': poly.STATEABBR = 'JA'
        elif poly.STATEFP == '20': poly.STATEABBR = 'KS'
        elif poly.STATEFP == '21': poly.STATEABBR = 'KY'
        elif poly.STATEFP == '89': poly.STATEABBR = 'KR'
        elif poly.STATEFP == '22': poly.STATEABBR = 'LA'
        elif poly.STATEFP == '23': poly.STATEABBR = 'ME'
        elif poly.STATEFP == '68': poly.STATEABBR = 'MH'
        elif poly.STATEFP == '24': poly.STATEABBR = 'MD'
        elif poly.STATEFP == '25': poly.STATEABBR = 'MA'
        elif poly.STATEFP == '26': poly.STATEABBR = 'MI'
        elif poly.STATEFP == '71': poly.STATEABBR = '71'
        elif poly.STATEFP == '27': poly.STATEABBR = 'MN'
        elif poly.STATEFP == '28': poly.STATEABBR = 'MS'
        elif poly.STATEFP == '29': poly.STATEABBR = 'MO'
        elif poly.STATEFP == '30': poly.STATEABBR = 'MT'
        elif poly.STATEFP == '76': poly.STATEABBR = '76'
        elif poly.STATEFP == '31': poly.STATEABBR = 'NE'
        elif poly.STATEFP == '32': poly.STATEABBR = 'NV'
        elif poly.STATEFP == '33': poly.STATEABBR = 'NH'
        elif poly.STATEFP == '34': poly.STATEABBR = 'NJ'
        elif poly.STATEFP == '35': poly.STATEABBR = 'NM'
        elif poly.STATEFP == '36': poly.STATEABBR = 'NY'
        elif poly.STATEFP == '37': poly.STATEABBR = 'NC'
        elif poly.STATEFP == '38': poly.STATEABBR = 'ND'
        elif poly.STATEFP == '69': poly.STATEABBR = 'MP'
        elif poly.STATEFP == '39': poly.STATEABBR = 'OH'
        elif poly.STATEFP == '40': poly.STATEABBR = 'OK'
        elif poly.STATEFP == '41': poly.STATEABBR = 'OR'
        elif poly.STATEFP == '70': poly.STATEABBR = 'PW'
        elif poly.STATEFP == '95': poly.STATEABBR = '95'
        elif poly.STATEFP == '42': poly.STATEABBR = 'PA'
        elif poly.STATEFP == '72': poly.STATEABBR = 'PR'
        elif poly.STATEFP == '44': poly.STATEABBR = 'RI'
        elif poly.STATEFP == '45': poly.STATEABBR = 'SC'
        elif poly.STATEFP == '46': poly.STATEABBR = 'SD'
        elif poly.STATEFP == '47': poly.STATEABBR = 'TN'
        elif poly.STATEFP == '48': poly.STATEABBR = 'TX'
        elif poly.STATEFP == '74': poly.STATEABBR = 'UM'
        elif poly.STATEFP == '49': poly.STATEABBR = 'UT'
        elif poly.STATEFP == '50': poly.STATEABBR = 'VT'
        elif poly.STATEFP == '51': poly.STATEABBR = 'VA'
        elif poly.STATEFP == '78': poly.STATEABBR = 'VI'
        elif poly.STATEFP == '79': poly.STATEABBR = '79'
        elif poly.STATEFP == '53': poly.STATEABBR = 'WA'
        elif poly.STATEFP == '54': poly.STATEABBR = 'WV'
        elif poly.STATEFP == '55': poly.STATEABBR = 'WI'
        elif poly.STATEFP == '56': poly.STATEABBR = 'WY'
        else:
            print(poly.STATEFP)
        poly.save()


def add_polygons():
    # Sort AHJs to at least make cure they are grouped by state.
    ahjs = AHJ.objects.order_by('address__StateProvince')
    polygons = Polygon.objects.all()

    i = 1
    # Counter for how many times we refiltered by state
    state_refilter_count = 1

    with open('potential_duplicates.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['AHJID', 'AHJName', 'StateProvince'])

        # Track what state we should filter for
        current_state_abbr = Address.objects.get(AHJ=ahjs.first()).StateProvince

        # Hold the counties and places of the current state
        temp_polygons = polygons.filter(STATEABBR=current_state_abbr).order_by('NAMELSAD')

        # For each ahj, give it a place and/or county
        # Record the ahjs that are potential duplicates
        for ahj in ahjs:

            # Get the ahj's address to filter by state
            address = Address.objects.get(AHJ=ahj)

            # Check if we need to filter by another state now
            temp_state_abbr = address.StateProvince
            if current_state_abbr != temp_state_abbr:
                current_state_abbr = temp_state_abbr
                temp_polygons = polygons.filter(STATEABBR=current_state_abbr).order_by('NAMELSAD')
                print('Refilter by state %i for %s' % (state_refilter_count, current_state_abbr))
                state_refilter_count += 1

            polygon = None
            polygon_index = binary_search(temp_polygons, ahj.AHJName)

            if polygon_index != -1:
                polygon = temp_polygons[polygon_index]

            if polygon is not None:
                if ahj.mpoly is not None:
                    # Write potential duplicates
                    writer.writerow([ahj.AHJID, ahj.AHJName, address.StateProvince])
                else:
                    ahj.mpoly = polygon
                    ahj.save()
                    print('Set polygon ' + polygon.NAMELSAD + ', ' + polygon.STATEABBR + ' as the polygon for ' + ahj.AHJName)
                    i += 1

            print('Count: %i' % i)


def clear_ahj_polygon_assignment():
    ahjs = AHJ.objects.all().order_by('address__StateProvince')
    i = 1
    for ahj in ahjs:
        ahj.county_mpoly = None
        ahj.city_mpoly = None
        ahj.save()
        print('Cleared mpoly of ' + ahj.AHJName)
        print('AHJ %i done' % i)
        i += 1


def merge_county_city():
    i = 1
    counties = County.objects.all()
    cities = City.objects.all()
    for c in counties:
        Polygon.objects.create(STATEFP=c.STATEFP, STATEABBR=c.STATEABBR, POLYFP=c.COUNTYFP, POLYNS=c.COUNTYNS,
                               GEOID=c.GEOID, NAME=c.NAME, NAMELSAD=c.NAMELSAD, LSAD=c.LSAD, CLASSFP=c.CLASSFP,
                               MTFCC=c.MTFCC, FUNCSTAT=c.FUNCSTAT, ALAND=c.ALAND, AWATER=c.AWATER, INTPTLAT=c.INTPTLAT,
                               INTPTLON=c.INTPTLON, mpoly=c.mpoly, CSAFP=c.CSAFP, CBSAFP=c.CBSAFP, METDIVFP=c.METDIVFP)
        print('%i Created Polygon for County: %s' % (i, c.NAMELSAD))
        i += 1
    for c in cities:
        Polygon.objects.create(STATEFP=c.STATEFP, STATEABBR=c.STATEABBR, POLYFP=c.PLACEFP, POLYNS=c.PLACENS,
                               GEOID=c.GEOID, NAME=c.NAME, NAMELSAD=c.NAMELSAD, LSAD=c.LSAD, CLASSFP=c.CLASSFP,
                               MTFCC=c.MTFCC, FUNCSTAT=c.FUNCSTAT, ALAND=c.ALAND, AWATER=c.AWATER, INTPTLAT=c.INTPTLAT,
                               INTPTLON=c.INTPTLON, mpoly=c.mpoly, PCICBSA=c.PCICBSA, PCINECTA=c.PCINECTA)
        print('%i Created Polygon for City: %s' % (i, c.NAMELSAD))
        i += 1


def merge_state():
    states = State.objects.all()
    for s in states:
        Polygon.objects.create(STATEFP=s.STATEFP, STATEABBR=s.STUSPS, POLYFP=s.STATEFP, POLYNS=s.STATENS,
                               GEOID=s.GEOID, NAME=s.NAME, NAMELSAD=s.NAME, LSAD=s.LSAD, CLASSFP='',
                               MTFCC=s.MTFCC, FUNCSTAT=s.FUNCSTAT, ALAND=s.ALAND, AWATER=s.AWATER, INTPTLAT=s.INTPTLAT,
                               INTPTLON=s.INTPTLON, mpoly=s.mpoly, REGION=s.REGION, DIVISION=s.DIVISION)


# Iterative Binary Search Function
# It returns index of x in given array arr if present,
# else returns -1
def binary_search(arr, x):
    low = 0
    high = len(arr) - 1
    mid = 0
    x = x.lower()

    while low <= high:
        mid = (high + low) // 2
        # Check if x is present at mid
        if arr[mid].NAMELSAD.lower() < x:
            low = mid + 1

        # If x is greater, ignore left half
        elif arr[mid].NAMELSAD.lower() > x:
            high = mid - 1

        # If x is smaller, ignore right half
        else:
            return mid

            # If we reach here, then the element was not present
    return -1


def assign_ahj_county():
    ahjs = AHJ.objects.filter(mpoly__GEOID__regex=r'^[0-9]{7}$').exclude(address__StateProvince='AK').order_by('address__StateProvince')
    counties = County.objects.all()
    current_state_abbr = ''
    i = 1
    for ahj in ahjs:

        # Get the ahj's address to filter by state
        address = Address.objects.get(AHJ=ahj)

        # Check if we need to filter by another state now
        temp_state_abbr = address.StateProvince
        if current_state_abbr != temp_state_abbr:
            current_state_abbr = temp_state_abbr
            print('filtering to %s' % current_state_abbr)
            counties_temp = counties.filter(STATEABBR=current_state_abbr)

        geoid = ahj.mpoly.GEOID
        city = City.objects.get(GEOID=geoid)
        contains_count = 0
        containing_county = None
        for county in counties_temp:
            print('checking %s' % county.NAMELSAD)
            if county.mpoly.contains(city.mpoly):
                contains_count += 1
                print('contained')
                containing_county = county
        if contains_count == 1:
            address.County = containing_county.NAMELSAD
            address.save()
        else:
            print('failed')
            print(city.NAMELSAD)
        print(current_state_abbr + " %i" % i)
        i += 1
