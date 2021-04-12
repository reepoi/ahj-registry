import json, csv
from .models import *


def modify_backup():
    model_keep_list = set(
        [
            'ahj_gis.polygon',
        ]
    )
    drop_list = set()
    obj = open('../utility_scripts/ahj_registry_backup.json')
    obj_json = json.loads(obj.read())
    obj.close()
    temp_arr = []
    for item in obj_json:
        if item['model'] in model_keep_list and len(item['fields']['GEOID']) == 2:
            temp_arr.append(item)
    result_str = json.dumps(temp_arr, indent=4)
    result_obj = open('../utility_scripts/statepolygons.json', 'w')
    result_obj.write(result_str)
    result_obj.close()


def insert_ahj_from_csv():
    with open('../utility_scripts/ahjdata.csv', newline='') as file:
        reader = csv.DictReader(file, delimiter=',', quotechar='"')
        i = 0
        total = 43096
        for row in reader:
            addr = Address.objects.create(
                AddrLine1=row['AddrLine1'],
                AddrLine2=row['AddrLine2'],
                AddrLine3=row['AddrLine3'],
                City=row['City'],
                Country=row['Country'],
                County=row['County'],
                StateProvince=row['StateProvince'],
                ZipPostalCode=row['ZipPostalCode'],
                Description=row['Description'],
                AddressType=row['AddressType']
            )
            AHJ.objects.create(
                AHJID=row['AHJID'],
                AHJCode=row['AHJCode'],
                AddressID=addr,
                AHJName=row['AHJName'],
                Description=row['Description'],
                DocumentSubmissionMethodNotes=row['DocumentSubmissionMethodNotes'],
                FileFolderURL=row['FileFolderURL'],
                URL=row['URL'],
                BuildingCode=row['BuildingCode'],
                BuildingCodeNotes=row['BuildingCodeNotes'],
                ElectricCode=row['ElectricCode'],
                ElectricCodeNotes=row['ElectricCodeNotes'],
                FireCode=row['FireCode'],
                FireCodeNotes=row['FireCodeNotes'],
                ResidentialCode=row['ResidentialCode'],
                ResidentialCodeNotes=row['ResidentialCodeNotes'],
                WindCode=row['WindCode'],
                WindCodeNotes=row['WindCodeNotes'],
                AHJLevelCode=row['AHJLevelCode']
            )
            i += 1
            print("insert_ahj_from_csv: {0:.0%}".format(i / total))


def insert_state():
    state_file = open('../utility_scripts/statepolygons.json')
    state_json = json.loads(state_file.read())
    state_file.close()
    i = 0
    total = len(state_json)
    for state in state_json:
        fields = state['fields']
        poly = Polygon.objects.create(Name=fields['NAME'],
                                      GEOID=fields['GEOID'],
                                      Polygon=fields['mpoly'],
                                      LandArea=fields['ALAND'],
                                      WaterArea=fields['AWATER'],
                                      InternalPLatitude=fields['INTPTLAT'],
                                      InternalPLongitude=fields['INTPTLON'])
        StatePolygon.objects.create(PolygonID=poly,
                                    FIPSCode=fields['STATEFP'])
        i += 1
        print("insert_state: {0:.0%}".format(i/total))


def insert_other():
    file = open('../utility_scripts/countycitypolygons.json')
    js = json.loads(file.read())
    file.close()
    i = 0
    total = len(js)
    for item in js:
        fields = item['fields']
        state = StatePolygon.objects.get(FIPSCode=fields['STATEFP'])
        if len(fields['GEOID']) == 5:
            poly = Polygon.objects.create(Name=fields['NAME'],
                                          GEOID=fields['GEOID'],
                                          Polygon=fields['mpoly'],
                                          LandArea=fields['ALAND'],
                                          WaterArea=fields['AWATER'],
                                          InternalPLatitude=fields['INTPTLAT'],
                                          InternalPLongitude=fields['INTPTLON'])
            CountyPolygon.objects.create(PolygonID=poly,
                                         StatePolygonID=state,
                                         LSAreaCodeName=fields['NAMELSAD'])
        elif len(fields['GEOID']) == 7:
            poly = Polygon.objects.create(Name=fields['NAME'],
                                          GEOID=fields['GEOID'],
                                          Polygon=fields['mpoly'],
                                          LandArea=fields['ALAND'],
                                          WaterArea=fields['AWATER'],
                                          InternalPLatitude=fields['INTPTLAT'],
                                          InternalPLongitude=fields['INTPTLON'])
            CityPolygon.objects.create(PolygonID=poly,
                                       StatePolygonID=state,
                                       LSAreaCodeName=fields['NAMELSAD'])
        i += 1
        print("insert_other: {0:.0%}".format(i/total))


state_fips_to_abbr = {
    '01': 'AL',
    '02': 'AK',
    '60': 'AS',
    '04': 'AZ',
    '05': 'AR',
    '81': 'BI',
    '06': 'CA',
    '08': 'CO',
    '09': 'CT',
    '10': 'DE',
    '11': 'DC',
    '12': 'FL',
    '64': 'FM',
    '13': 'GA',
    '66': 'GU',
    '15': 'HI',
    '16': 'ID',
    '17': 'IL',
    '18': 'IN',
    '19': 'IA',
    '86': 'JI',
    '67': 'JA',
    '20': 'KS',
    '21': 'KY',
    '89': 'KR',
    '22': 'LA',
    '23': 'ME',
    '68': 'MH',
    '24': 'MD',
    '25': 'MA',
    '26': 'MI',
    '71': '71',  # Territory abbr collides with state abbr
    '27': 'MN',
    '28': 'MS',
    '29': 'MO',
    '30': 'MT',
    '76': '76',  # Territory abbr collides with state abbr
    '31': 'NE',
    '32': 'NV',
    '33': 'NH',
    '34': 'NJ',
    '35': 'NM',
    '36': 'NY',
    '37': 'NC',
    '38': 'ND',
    '69': 'MP',
    '39': 'OH',
    '40': 'OK',
    '41': 'OR',
    '70': 'PW',
    '95': '95',  # Territory abbr collides with state abbr
    '42': 'PA',
    '72': 'PR',
    '44': 'RI',
    '45': 'SC',
    '46': 'SD',
    '47': 'TN',
    '48': 'TX',
    '74': 'UM',
    '49': 'UT',
    '50': 'VT',
    '51': 'VA',
    '78': 'VI',
    '53': 'WA',
    '54': 'WV',
    '55': 'WI',
    '56': 'WY'
}

abbr_to_state_fips = dict(map(reversed, state_fips_to_abbr.items()))


def pair_polygons(model):
    polgyons = model.objects.all()
    ahjs = AHJ.objects.filter(PolygonID=None).order_by('AddressID__StateProvince')
    i = 0
    total = len(ahjs)
    # Pair polygons
    current_state_fips = ''
    temp_polygons = model.objects.none()
    for ahj in ahjs:
        addr = Address.objects.get(AddressID=ahj.AddressID.AddressID)
        temp_state_fips = abbr_to_state_fips[addr.StateProvince]
        if current_state_fips != temp_state_fips:
            current_state_fips = temp_state_fips
            temp_polygons = polgyons.filter(PolygonID__GEOID__startswith=current_state_fips).order_by('LSAreaCodeName')
        polygon_index = binary_search(temp_polygons, ahj.AHJName)
        if polygon_index != -1:
            polygon = temp_polygons[polygon_index]
            ahj.PolygonID = polygon.PolygonID
            ahj.save()
        i += 1
        print("pair_polygons_ahjs {1}: {0:.0%}".format(i/total), model.__name__)


def pair_state_polygons():
    # Pair states
    states = StatePolygon.objects.all()
    i = 0
    total = len(states)
    for state in states:
        ahj = AHJ.objects.get(AHJName=state.PolygonID.Name + ' state')
        ahj.PolygonID = state.PolygonID
        ahj.save()
        i += 1
        print("pair_polygons_ahjs {1}: {0:.0%}".format(i/total), StatePolygon.__name__)


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
        if arr[mid].LSAreaCodeName.lower() < x:
            low = mid + 1

        # If x is greater, ignore left half
        elif arr[mid].LSAreaCodeName.lower() > x:
            high = mid - 1

        # If x is smaller, ignore right half
        else:
            return mid

            # If we reach here, then the element was not present
    return -1


def insert_all():
    insert_state()
    insert_other()
    insert_ahj_from_csv()


def pair_all():
    pair_polygons(CountyPolygon)
    pair_polygons(CityPolygon)
    pair_polygons(CountySubdivisionPolygon)
    pair_state_polygons()
