import csv
import os
from functools import lru_cache
import datetime
from django.apps import apps
from django.contrib.gis.utils import LayerMapping
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import URLValidator

from .models import *
from .models_field_enums import *

BASE_DIR = os.path.expanduser('~/AHJRegistryData/')
BASE_DIR_SHP = BASE_DIR + '2020CensusPolygons/'


state_mapping = {
    'GEOID': 'GEOID',
    'NAME': 'NAME',
    'ALAND': 'ALAND',
    'AWATER': 'AWATER',
    'INTPTLAT': 'INTPTLAT',
    'INTPTLON': 'INTPTLON',
    'mpoly': 'MULTIPOLYGON'
}


county_mapping = {
    'STATEFP': 'STATEFP',
    'GEOID': 'GEOID',
    'NAME': 'NAME',
    'NAMELSAD': 'NAMELSAD',
    'ALAND': 'ALAND',
    'AWATER': 'AWATER',
    'INTPTLAT': 'INTPTLAT',
    'INTPTLON': 'INTPTLON',
    'mpoly': 'MULTIPOLYGON'
}


cousub_mapping = {
    'STATEFP': 'STATEFP',
    'GEOID': 'GEOID',
    'NAME': 'NAME',
    'NAMELSAD': 'NAMELSAD',
    'ALAND': 'ALAND',
    'AWATER': 'AWATER',
    'INTPTLAT': 'INTPTLAT',
    'INTPTLON': 'INTPTLON',
    'mpoly': 'MULTIPOLYGON'
}


city_mapping = {
    'STATEFP': 'STATEFP',
    'GEOID': 'GEOID',
    'NAME': 'NAME',
    'NAMELSAD': 'NAMELSAD',
    'ALAND': 'ALAND',
    'AWATER': 'AWATER',
    'INTPTLAT': 'INTPTLAT',
    'INTPTLON': 'INTPTLON',
    'mpoly': 'MULTIPOLYGON'
}


def upload_all_shapefile_types():
    upload_state_shapefiles()
    upload_county_shapefiles()
    upload_city_shapefiles()
    upload_countysubdivision_shapefiles()


def upload_state_shapefiles():
    for subdir in os.walk(BASE_DIR_SHP + 'States'):
        for file in subdir[2]:
            if file.endswith('.shp'):
                state_shp = os.path.join(subdir[0], file)
                lm = LayerMapping(StateTemp, state_shp, state_mapping, transform=False)
                lm.save(strict=True, verbose=True)


def upload_county_shapefiles():
    for subdir in os.walk(BASE_DIR_SHP + 'Counties'):
        for file in subdir[2]:
            if file.endswith('.shp'):
                county_shp = os.path.join(subdir[0], file)
                lm = LayerMapping(CountyTemp, county_shp, county_mapping, transform=False)
                lm.save(strict=True, verbose=True)


def upload_city_shapefiles():
    for subdir in os.walk(BASE_DIR_SHP + 'Places'):
        for file in subdir[2]:
            if file.endswith('.shp'):
                city_shp = os.path.join(subdir[0], file)
                lm = LayerMapping(CityTemp, city_shp, city_mapping, transform=False)
                lm.save(strict=True, verbose=True)


def upload_countysubdivision_shapefiles():
    for subdir in os.walk(BASE_DIR_SHP + 'CountySubdivisions'):
        for file in subdir[2]:
            if file.endswith('.shp'):
                cousub_shp = os.path.join(subdir[0], file)
                lm = LayerMapping(CousubTemp, cousub_shp, cousub_mapping, transform=False)
                lm.save(strict=True, verbose=True)


def get_polygon_fields(obj):
    return {
        'Name': obj.NAME,
        'GEOID': obj.GEOID,
        'Polygon': obj.mpoly,
        'LandArea': obj.ALAND,
        'WaterArea': obj.AWATER,
        'InternalPLatitude': obj.INTPTLAT,
        'InternalPLongitude': obj.INTPTLON
    }


def get_state_polygon_type_fields(obj, polygon):
    return {
        'PolygonID': polygon,
        'FIPSCode': obj.GEOID
    }


def get_other_polygon_type_fields(obj, polygon):
    return {
        'PolygonID': polygon,
        'StatePolygonID': StatePolygon.objects.get(FIPSCode=obj.GEOID[:2]),
        'LSAreaCodeName': obj.NAMELSAD
    }


def translate_polygons():
    translate_states()
    translate_counties()
    translate_cities()
    translate_countysubdivisions()


def translate_states():
    states = StateTemp.objects.all()
    count = states.count()
    i = 0
    for state in states:
        polygon = Polygon.objects.create(**get_polygon_fields(state))
        StatePolygon.objects.create(**get_state_polygon_type_fields(state, polygon))
        print("pair_polygons_ahjs {1}: {0:.0%}".format(i/count, StateTemp.__name__))
        i += 1


def translate_counties():
    counties = CountyTemp.objects.all()
    count = counties.count()
    i = 0
    for county in counties:
        polygon = Polygon.objects.create(**get_polygon_fields(county))
        CountyPolygon.objects.create(**get_other_polygon_type_fields(county, polygon))
        print("pair_polygons_ahjs {1}: {0:.0%}".format(i/count, CountyTemp.__name__))
        i += 1


def translate_cities():
    cities = CityTemp.objects.all()
    count = cities.count()
    i = 0
    for city in cities:
        polygon = Polygon.objects.create(**get_polygon_fields(city))
        CityPolygon.objects.create(**get_other_polygon_type_fields(city, polygon))
        print("pair_polygons_ahjs {1}: {0:.0%}".format(i/count, CityPolygon.__name__))
        i += 1


def translate_countysubdivisions():
    cousubs = CousubTemp.objects.all()
    count = cousubs.count()
    i = 0
    for cousub in cousubs:
        polygon = Polygon.objects.create(**get_polygon_fields(cousub))
        CountySubdivisionPolygon.objects.create(**get_other_polygon_type_fields(cousub, polygon))
        print("pair_polygons_ahjs {1}: {0:.0%}".format(i/count, CountySubdivisionPolygon.__name__))
        i += 1


ENUM_FIELDS = {
    'BuildingCode',
    'ElectricCode',
    'FireCode',
    'ResidentialCode',
    'WindCode',
    'AHJLevelCode',
    'DocumentSubmissionMethod',
    'PermitIssueMethod',
    'AddressType',
    'LocationDeterminationMethod',
    'LocationType',
    'ContactType',
    'PreferredContactMethod',
    'EngineeringReviewType',
    'RequirementLevel',
    'StampType',
    'FeeStructureType',
    'InspectionType'
}

ENUM_PLURALS_TRANSLATE = {
    'DocumentSubmissionMethods': 'DocumentSubmissionMethod',
    'PermitIssueMethods': 'PermitIssueMethod'
}


def add_enum_values():
    """
    Adds all enum values to their enum tables.
    """
    for field in ENUM_FIELDS:
        model = apps.get_model('ahj_app', field)
        model.objects.all().delete()
        model.objects.bulk_create(list(map(lambda choice: model(Value=choice[0]),
                                           model._meta.get_field('Value').choices)))


def is_zero_depth_field(name):
    """
    Checks if a field name has one dot in it.
    For example, BuildingCode.Value
    """
    if name.find('.') != -1 and name.find('.') == name.rfind('.'):
        return True
    return False


def dict_filter_keys_start_with(start, row):
    """
    Given a dict, returns a new dict with key-value pairs
    where the key of each pair starts with start.
    """
    return {k[len(start)+1:]: v for k, v in row.items() if k.startswith(start)}


def build_field_val_dict(row):
    """
    Builds an Orange Button AuthorityHavingJurisdiction JSON object from a flattened object.
    """
    result = {}
    done_keys = set()
    for k, v in row.items():
        field = k[:k.find('.')]
        if k == '' or v == '' or field in done_keys:  # no value or already gathered to create a dict
            continue
        elif field == 'AHJLevelCode':
            result[field] = '0' + v if len(v) < 3 else v 
        elif is_zero_depth_field(k):  # (key, value or array of values) pair
            square_loc = field.find('[')
            if square_loc >= 0:
                array_field = field[:square_loc]
                if array_field not in result:
                    result[array_field] = []
                result[array_field].append(v)
            else:
                result[field] = v
        else:  # (key, object or array of objects) pair
            subrow = dict_filter_keys_start_with(field, row)
            done_keys.add(field)
            square_loc = field.find('[')
            if square_loc >= 0:
                array_field = field[:square_loc]
                if array_field not in result:
                    result[array_field] = []
                result[array_field].append(build_field_val_dict(subrow))
            else:
                result[field] = build_field_val_dict(subrow)
    return result


def create_address(address_dict):
    location_dict = address_dict.pop('Location', None)
    if location_dict is not None:
        address_dict['LocationID'] = create_location(location_dict)
    return Address.objects.create(**address_dict)


def create_location(location_dict):
    return Location.objects.create(**location_dict)


def create_contact(contact_dict):
    address_dict = contact_dict.pop('Address', None)
    if address_dict is not None:
        contact_dict['AddressID'] = create_address(address_dict)
    else:
        contact_dict['AddressID'] = Address.objects.create()
    return Contact.objects.create(**contact_dict)


@lru_cache(maxsize=None)
def get_enum_value_row(enum_field, enum_value):
    """
    Finds the row of the enum table given the field name and its enum value.
    """
    # Translate plural, if given
    enum_field = ENUM_PLURALS_TRANSLATE[enum_field] if enum_field in ENUM_PLURALS_TRANSLATE else enum_field
    return apps.get_model('ahj_app', enum_field).objects.get(Value=enum_value)


def enum_values_to_primary_key(ahj_dict):
    """
    Replace enum values in a dict with the row of the value in its enum model.
    For example, '2021IBC' => BuildingCode.objects.get(Value='2021IBC')
    """
    for field in ahj_dict:
        if type(ahj_dict[field]) is dict:
            ahj_dict[field] = enum_values_to_primary_key(ahj_dict[field])
        elif type(ahj_dict[field]) is list:
            for i in range(len(ahj_dict[field])):
                if type(ahj_dict[field][i]) is dict:
                    ahj_dict[field][i] = enum_values_to_primary_key(ahj_dict[field][i])
                else:  # Array of enum values
                    ahj_dict[field][i] = get_enum_value_row(field, ahj_dict[field][i])
        else:
            if field in ENUM_FIELDS:
                ahj_dict[field] = get_enum_value_row(field, ahj_dict[field])
    return ahj_dict


def create_edit_objects(ahj_obj, field_string, userID, DSC, newVal):
    """
    Currently only creates edits for string fields on an AHJ.
    This is a helper for adding DataSourceComments.
    """
    edit_dict = {}
    edit_dict['AHJPK'] = ahj_obj
    edit_dict['SourceTable'] = 'AHJ'
    edit_dict['SourceColumn'] = field_string
    edit_dict['SourceRow'] = ahj_obj.AHJPK
    edit_dict['OldValue'] = ''
    edit_dict['NewValue'] = newVal
    edit_dict['DateRequested'] = datetime.date.today() - datetime.timedelta(days=1)
    edit_dict['DateEffective'] = datetime.date.today() - datetime.timedelta(days=1)
    edit_dict['ReviewStatus'] = 'A'
    edit_dict['ChangedBy'] = userID
    edit_dict['DataSourceComment'] = DSC
    edit_dict['EditType'] = 'U'
    return Edit.objects.create(**edit_dict)


def create_admin_user():
    admin_username = settings.ADMIN_ACCOUNT_USERNAME
    admin_email = settings.ADMIN_ACCOUNT_EMAIL
    admin_password = settings.ADMIN_ACCOUNT_PASSWORD
    admin = User.objects.create_user(
        Username=admin_username,
        Email=admin_email,
        password=admin_password
    )
    admin.is_active = True
    admin.is_staff = True
    admin.save()
    webpage_api_token = WebpageToken.objects.create(user=admin)
    api_token = APIToken.objects.create(user=admin)
    print(f'WEBPAGE API TOKEN: {webpage_api_token}')
    print(f'API TOKEN: {api_token}')


def drop_related_id_columns(ahj_csv_row):
    """
    Helper method for the clean_ahj_data_csv method below.
    It removes:
     - The primary key columns of related objects such as
    Address, Contact, and EngieeringReviewRequirement.
    """
    COLUMNS_TO_DROP = (
        'AddressID.Value',
        'ContactID.Value',
        'EngineeringReviewRequirementID.Value',
        'LocationID.Value'
    )
    return {k: v for k, v in ahj_csv_row.items() if not k.endswith(COLUMNS_TO_DROP)}


def remove_non_orange_button_code_years(ahj_csv_row):
    """
    Helper method for the clean_ahj_data_csv method below.
    It removes:
     - Code years that do not fit Orange Button enumerations.
    """
    AHJ_CODE_YEAR_FIELDS = {
        'BuildingCode',
        'ElectricCode',
        'FireCode',
        'ResidentialCode',
        'WindCode'
    }
    for field in AHJ_CODE_YEAR_FIELDS:
        csv_value = ahj_csv_row[f'{field}.Value']
        try:
            if csv_value != '':
                get_enum_value_row(field, csv_value)
        except ObjectDoesNotExist:
            ahj_csv_row[f'{field}.Value'] = ''


def fix_contact_title_field_from_csv_bug(ahj_csv_row):
    """
    Helper method for the clean_ahj_data_csv method below.
    It removes:
     - Fixes the Contact Title field that does not export correctly due to a bug in the csv export.
    Only works if the AHJ has one Contact.
    """
    CSV_CONTACT_BUG_FIELD = 'Contacts[{0}].Title.Value'
    CSV_CONTACT_BUG_AFFECTED_FIELDS = {
        'Title': 'Contacts[{0}].Title.Value',
        'PreferredContactMethod': 'Contacts[{0}].PreferredContactMethod.Value',
        'URL': 'Contacts[{0}].URL.Value',
        'DocumentSubmissionMethod': 'DocumentSubmissionMethods[0].Value',
        'PermitIssueMethod': 'PermitIssueMethods[0].Value'
    }
    url_validator = URLValidator()
    i = 0
    while ahj_csv_row.get(CSV_CONTACT_BUG_FIELD.format(i), '') != '' and ahj_csv_row.get(CSV_CONTACT_BUG_FIELD.format(1), '') == '':
        title_field = CSV_CONTACT_BUG_AFFECTED_FIELDS['Title'].format(i)
        ahj_csv_row[title_field] = ahj_csv_row[title_field].strip()
        # Check PreferredContactMethod is valid
        pcm_field = CSV_CONTACT_BUG_AFFECTED_FIELDS['PreferredContactMethod'].format(i)
        try:
            if ahj_csv_row[pcm_field] == '' or get_enum_value_row('PreferredContactMethod', ahj_csv_row[pcm_field]) is not None:
                i += 1
                continue
        except ObjectDoesNotExist:
            ahj_csv_row[title_field] += f', {ahj_csv_row[pcm_field].strip()}'
            ahj_csv_row[pcm_field] = ''
        # Check URL is valid
        url_field = CSV_CONTACT_BUG_AFFECTED_FIELDS['URL'].format(i)
        try:
            if ahj_csv_row[url_field] == '':
                i += 1
                continue
            url_validator(ahj_csv_row[url_field])
            i += 1
            continue
        except ValidationError:
            ahj_csv_row[title_field] += f', {ahj_csv_row[url_field].strip()}'
            ahj_csv_row[url_field] = ''
        # Check DocumentSubmissionMethod is valid
        dsm_field = CSV_CONTACT_BUG_AFFECTED_FIELDS['DocumentSubmissionMethod']
        try:
            if ahj_csv_row[dsm_field] == '' or get_enum_value_row('DocumentSubmissionMethod', ahj_csv_row[dsm_field]) is not None:
                i += 1
                continue
        except ObjectDoesNotExist:
            ahj_csv_row[title_field] += f', {ahj_csv_row[dsm_field].strip()}'
            ahj_csv_row[dsm_field] = ''
        # Check PermitIssueMethod is valid
        pim_field = CSV_CONTACT_BUG_AFFECTED_FIELDS['PermitIssueMethod']
        try:
            if ahj_csv_row[pim_field] == '' or get_enum_value_row('PermitIssueMethod', ahj_csv_row[pim_field]) is not None:
                i += 1
                continue
        except ObjectDoesNotExist:
            ahj_csv_row[title_field] += f', {ahj_csv_row[pim_field].strip()}'
            ahj_csv_row[pim_field] = ''
        i += 1


def clean_ahj_data_csv(csv_path=(BASE_DIR + 'AHJRegistryData/ahjregistrydata.csv')):
    """
    Specialized method to clean parts of a CSV with AHJ data.
    It removes:
     - Code years that do not fit Orange Button enumerations.
     - Fixes the Contact Title field that does not export correctly due to a bug in the csv export.
    """
    result_rows = []
    with open(csv_path) as file:
        i = 1
        reader = csv.DictReader(file, delimiter=',', quotechar='"')
        for row in reader:
            row = {k: v for k, v in row.items() if k is not None}
            row = drop_related_id_columns(row)
            fix_contact_title_field_from_csv_bug(row)
            remove_non_orange_button_code_years(row)
            result_rows.append(row)
            print('AHJ {0}: {1}'.format(row["AHJID.Value"], i))
            i += 1
    if len(result_rows) > 0:
        column_names = result_rows[0].keys()
        new_file_name = csv_path[:-4] + '_cleaned.csv'
        column_names_dict = {k: k for k in column_names}
        with open(new_file_name, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=column_names)
            writer.writerow(column_names_dict)
            for row in result_rows:
                writer.writerow(row)


def load_ahj_data_csv(csv_path=(BASE_DIR + 'AHJRegistryData/ahjregistrydata.csv')):
#    create_admin_user()
    user = User.objects.get(Email=settings.ADMIN_ACCOUNT_EMAIL)
    with open(csv_path) as file:
        reader = csv.DictReader(file, delimiter=',', quotechar='"')
        i = 1
        for row in reader:
            ahj_dict = build_field_val_dict(row)
            enum_values_to_primary_key(ahj_dict)

            address_dict = ahj_dict.pop('Address', None)
            if address_dict is not None:
                ahj_dict['AddressID'] = create_address(address_dict)
            else:
                ahj_dict['AddressID'] = Address.objects.create()

            dsc = ahj_dict.pop('DataSourceComments', '')
            dsms = ahj_dict.pop('DocumentSubmissionMethods', [])
            pims = ahj_dict.pop('PermitIssueMethods', [])
            errs = ahj_dict.pop('EngineeringReviewRequirements', [])
            contacts_dict = ahj_dict.pop('Contacts', [])

            ahj = AHJ.objects.create(**ahj_dict)

            for contact_dict in contacts_dict:
                contact_dict['ParentTable'] = 'AHJ'
                contact_dict['ParentID'] = ahj.AHJPK
                contact_dict['ContactStatus'] = True
                create_contact(contact_dict)

            for dsm in dsms:
                AHJDocumentSubmissionMethodUse.objects.create(AHJPK=ahj, DocumentSubmissionMethodID=dsm, MethodStatus=1)

            for pim in pims:
                AHJPermitIssueMethodUse.objects.create(AHJPK=ahj, PermitIssueMethodID=pim, MethodStatus=1)

            for err in errs:
                err['AHJPK'] = ahj
                err['EngineeringReviewRequirementStatus'] = 1
                EngineeringReviewRequirement.objects.create(**err)

            if dsc != '':
                if ahj.BuildingCode is not None:
                    bcVal = BuildingCode.objects.get(BuildingCodeID=ahj.BuildingCode.BuildingCodeID).Value
                    create_edit_objects(ahj, 'BuildingCode', user, dsc, bcVal)

                if ahj.FireCode is not None:
                    fcVal = FireCode.objects.get(FireCodeID=ahj.FireCode.FireCodeID).Value
                    create_edit_objects(ahj, 'FireCode', user, dsc, fcVal)

                if ahj.ResidentialCode is not None:
                    rcVal = ResidentialCode.objects.get(ResidentialCodeID=ahj.ResidentialCode.ResidentialCodeID).Value
                    create_edit_objects(ahj, 'ResidentialCode', user, dsc, rcVal)

                if ahj.ElectricCode is not None:
                    ecVal = ElectricCode.objects.get(ElectricCodeID=ahj.ElectricCode.ElectricCodeID).Value
                    create_edit_objects(ahj, 'ElectricCode', user, dsc, ecVal)

                if ahj.WindCode is not None:
                    wcVal = WindCode.objects.get(WindCodeID=ahj.WindCode.WindCodeID).Value
                    create_edit_objects(ahj, 'WindCode', user, dsc, wcVal)

            print('AHJ {0}: {1}'.format(ahj.AHJID, i))
            i += 1


def update_location(address, location_dict):
    """
    Updates non-related fields on the Location model given a dict.
    The dict is expected to contain only the fields to be updated.
    Returns an array of messages about the update.
    """
    update_messages = []
    if location_dict is None:
        return update_messages
    if address.LocationID is None:
        address.LocationID = Location.objects.create(**location_dict)
        address.save()
    else:
        Location.objects.filter(LocationID=address.LocationID.LocationID).update(**location_dict)
    return update_messages


def update_address(parent, address_dict):
    """
    Updates non-related fields on the Address model given a dict.
    If the contacts have an Location, the Location will also be updated.
    The dict is expected to contain only the fields to be updated.
    Returns an array of messages about the update.
    """
    update_messages = []
    if address_dict is None:
        return update_messages
    location_dict = address_dict.pop('Location', None)
    if parent.AddressID is None:
        parent.AddressID = Address.objects.create(**address_dict)
        parent.save()
    else:
        Address.objects.filter(AddressID=parent.AddressID.AddressID).update(**address_dict)
    update_messages += update_location(parent.AddressID, location_dict)
    return update_messages


def update_contacts(ahj, parent, contacts_dict_array):
    """
    Updates non-related fields on the Contact model given an array of dicts.
    If the Contacts have an Address, the Address will also be updated.
    The dict is expected to contain only the fields to be updated.
    Returns an array of messages about the update.
    NOTE: Will update only if the AHJ has one contact.
    """
    update_messages = []
    current_contacts = Contact.objects.filter(ParentTable=parent.__class__.__name__, ParentID=ahj.AHJPK)
    if len(contacts_dict_array) > 1 or current_contacts.count() > 1:
        update_messages.append(f'HAS MORE THAN ONE CONTACT: {ahj.AHJID}\n')
    elif len(contacts_dict_array) == 1:
        address = contacts_dict_array[0].pop('Address', None)
        current_contacts.update(**contacts_dict_array[0])
        update_messages += update_address(current_contacts.first(), address)
    return update_messages


def update_document_submission_methods(ahj, dsms_value_array):
    """
    Updates non-related fields on the PermitIssueMethod model given an array of values.
    Returns an array of messages about the update.
    """
    update_messages = []
    for dsm in dsms_value_array:
        dsm_row = get_enum_value_row('DocumentSubmissionMethod', dsm)
        AHJDocumentSubmissionMethodUse.objects.update_or_create(AHJ=ahj, DocumentSubmissionMethodID=dsm_row, MethodStatus=True)
    return update_messages


def update_permit_issue_methods(ahj, pim_value_array):
    """
    Updates non-related fields on the PermitIssueMethod model given an array of values.
    Returns an array of messages about the update.
    """
    update_messages = []
    for pim in pim_value_array:
        pim_row = get_enum_value_row('PermitIssueMethod', pim)
        AHJPermitIssueMethodUse.objects.update_or_create(AHJ=ahj, PermitIssueMethodID=pim_row, MethodStatus=True)
    return update_messages


def update_engineering_review_requirements(ahj, errs_dict_array):
    """
    Updates non-related fields on the EngineeringReviewRequirement model given an array of dicts.
    The dict is expected to contain only the fields to be updated.
    Returns an array of messages about the update.
    NOTE: Will update only if the AHJ has one engineering review requirement.
    """
    update_messages = []
    current_errs = EngineeringReviewRequirement.objects.filter(AHJ=ahj)
    if len(errs_dict_array) > 1 or current_errs.count() > 1:
        update_messages.append(f'HAS MORE THAN ONE ENGINEERING REVIEW REQUIREMENT: {ahj.AHJID}\n')
    else:
        current_errs.update(**errs_dict_array[0])
    return update_messages


def update_fee_structures(ahj, fs_dict_array):
    """
    Updates non-related fields on the FeeStructure model given an array of dicts.
    The dict is expected to contain only the fields to be updated.
    Returns an array of messages about the update.
    NOTE: Does not update any fee structures.
    """
    update_messages = []
    current_fs = FeeStructure.objects.filter(AHJ=ahj)
    if len(fs_dict_array) > 0 or current_fs.count() > 0:
        update_messages.append(f'HAS FEE STRUCTURES: {ahj.AHJID}\n')
    return update_messages


def update_ahj_inspections(ahj, ai_dict_array):
    """
    Updates non-related fields on the AHJInspection model given an array of dicts.
    If the AHJInspections have a Contact, the Contact will also be updated.
    The dict is expected to contain only the fields to be updated.
    Returns an array of messages about the update.
    NOTE: Does not update any fee structures.
    """
    update_messages = []
    current_ai = AHJInspection.objects.filter(AHJ=ahj)
    if len(ai_dict_array) > 0 or current_ai.count() > 0:
        update_messages.append(f'HAS AHJ INSPECTIONS: {ahj.AHJID}\n')
    return update_messages


def update_ahj_fields(ahj, ahj_field_dict):
    """
    Updates non-related fields on the AHJ model given a dict.
    The dict is expected to contain only the fields to be updated.
    Returns an array of messages about the update.
    """
    update_messages = []
    AHJ.objects.filter(AHJPK=ahj.AHJPK).update(**ahj_field_dict)
    return update_messages


def update_edits_for_data_source_comments(ahj, dsc):
    """
    Specialized method to create edits for the building code years an AHJ has
    when the field DataSourceComments is provided.
    The user attributed to creating and approving these edits is the admin user.
    This assumes the DataSourceComments refers to the building code years.
    Returns an array of messages about the update.
    """
    update_messages = []
    if dsc is None:
        return update_messages
    edits = Edit.objects.filter(AHJPK=ahj, DataSourceComment=dsc)
    if not edits.exists():
        user = User.objects.get(Email=settings.ADMIN_ACCOUNT_EMAIL)
        if ahj.BuildingCode is not None:
            create_edit_objects(ahj, 'BuildingCode', user, dsc, ahj.BuildingCode.Value)

        if ahj.FireCode is not None:
            create_edit_objects(ahj, 'FireCode', user, dsc, ahj.FireCode.Value)

        if ahj.ResidentialCode is not None:
            create_edit_objects(ahj, 'ResidentialCode', user, dsc, ahj.ResidentialCode.Value)

        if ahj.ElectricCode is not None:
            create_edit_objects(ahj, 'ElectricCode', user, dsc, ahj.ElectricCode.Value)

        if ahj.WindCode is not None:
            create_edit_objects(ahj, 'WindCode', user, dsc, ahj.WindCode.Value)
    return update_messages


def update_ahj(ahj_dict):
    """
    Updates all fields on the AHJ model and related models given a dict.
    The dict is expected to contain only the fields to be updated.
    Returns an array of messages about the update.
    """
    update_messages = []
    try:
        ahj = AHJ.objects.get(AHJID=ahj_dict['AHJID'])
        update_messages += update_address(ahj, ahj_dict.pop('Address', None))
        update_messages += update_contacts(ahj, ahj, ahj_dict.pop('Contacts', []))
        update_messages += update_engineering_review_requirements(ahj, ahj_dict.pop('EngineeringReviewRequirements', []))
        update_messages += update_document_submission_methods(ahj, ahj_dict.pop('DocumentSubmissionMethods', []))
        update_messages += update_permit_issue_methods(ahj, ahj_dict.pop('PermitIssueMethods', []))
        update_messages += update_fee_structures(ahj, ahj_dict.pop('FeeStructures', []))
        update_messages += update_ahj_inspections(ahj, ahj_dict.pop('AHJInspections', []))
        update_messages += update_edits_for_data_source_comments(ahj, ahj_dict.pop('DataSourceComments', None))
        update_messages += update_ahj_fields(ahj, ahj_dict)
    except ObjectDoesNotExist:
        update_messages.append(f'NEW AHJ (NO UPDATES MADE): {ahj_dict["AHJID"]}\n')
    return update_messages


def update_ahj_data_csv(csv_path=(BASE_DIR + 'AHJRegistryData/ahjregistrydata.csv')):
    """
    Given a path to a CSV containing AHJ data, updates all AHJs to match the data in the CSV.
    If the data cannot be updated, it will write a message for manual review to a text file.
    """
    with open(csv_path) as file:
        update_messages = []
        i = 1
        reader = csv.DictReader(file, delimiter=',', quotechar='"')
        for row in reader:
            ahj_dict = build_field_val_dict(row)
            enum_values_to_primary_key(ahj_dict)
            update_messages += update_ahj(ahj_dict)
            print('AHJ {0}: {1}'.format(ahj_dict["AHJID"], i))
            i += 1
        with open(BASE_DIR + 'AHJRegistryData/ahj_data_manual_updates.txt', 'w') as manual_updates:
            manual_updates.writelines(update_messages)


def load_ahj_census_names_csv():
    """
    Save AHJ census names from a CSV with columns: (AHJID, AHJCensusName, StateProvince)
    """
    with open(BASE_DIR + 'AHJRegistryData/ahjcensusnames.csv') as file:
        reader = csv.DictReader(file, delimiter=',', quotechar='"')
        i = 1
        for row in reader:
            ahj = AHJ.objects.get(AHJID=row['AHJID'])
            AHJCensusName.objects.create(AHJPK=ahj,
                                         AHJCensusName=row['AHJCensusName'],
                                         StateProvince=row['StateProvince'])
            print('AHJ {0}: {1}'.format(ahj.AHJID, i))
            i += 1


def load_ahj_census_names_ahj_table():
    """
    Save AHJ census names are AHJ names.
    Use only if AHJ names are still AHJ census names.
    """
    i = 1
    for ahj in AHJ.objects.all():
        AHJCensusName.objects.create(AHJPK=ahj,
                                     AHJCensusName=ahj.AHJName,
                                     StateProvince=ahj.AddressID.StateProvince)
        print('AHJ {0}: {1}'.format(ahj.AHJID, i))
        i += 1


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


def pair_all():
    AHJ.objects.all().update(PolygonID=None)
    pair_polygons(CountyPolygon)
    pair_polygons(CityPolygon)
    pair_polygons(CountySubdivisionPolygon)
    pair_state_polygons()


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
        print("pair_polygons_ahjs {1}: {0:.0%}".format(i/total, model.__name__))


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
        print("pair_polygons_ahjs {1}: {0:.0%}".format(i/total, StatePolygon.__name__))


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


BASE_DIR_USER = BASE_DIR + 'UserData/'
def load_user_data_csv():
    users = {}

    # Get user information
    with open(BASE_DIR_USER + 'prod_core_user.csv') as file:
        reader = csv.DictReader(file, delimiter=',', quotechar='"')
        i = 1
        for row in reader:
            user = {}
            user['Email'] = row['email_address']
            user['password'] = row['password']
            user['Username'] = f'username{i}'
            user['FirstName'] = row['first_name']
            user['LastName'] = row['last_name']
            user['SignUpDate'] = row['date_joined'][:10]
            user['is_active'] = row['is_active']

            users[row['id']] = user
            i += 1

    with open(BASE_DIR_USER + 'prod_authtoken_token.csv') as file:
        reader = csv.DictReader(file, delimiter=',', quotechar='"')
        i = 1
        for row in reader:
            users[row['user_id']]['apitoken'] = row['key']
            print(users[row['user_id']])

    # Create users and api tokens
    i = 1
    for user in users.values():
        apitoken = user.pop('apitoken')
        firstname = user.pop('FirstName')
        lastname = user.pop('LastName')
        user['ContactID'] = Contact.objects.create(FirstName=firstname, LastName=lastname)
        user = User.objects.create(**user)
        APIToken.objects.create(key=apitoken, user=user)
        print('User {0}: {1}'.format(i, user))
        i += 1
