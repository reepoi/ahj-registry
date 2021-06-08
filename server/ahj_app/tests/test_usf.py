from ahj_app import usf
from django.apps import apps

import fixtures
import pytest


def csv_ahj_row_dict(custom_values_dict):
    """
    Returns one row of what a csv.DictReader returns for AHJ data in a CSV file.
    NOTE: does not contain all of the possible fields!
    """
    ahj_csv_dict = {
        'AHJID.Value': 'dd54221b-ac43-4bf1-98b-57af2a2ae1d',
        'AHJCode.Value': 'AK-06070',
        'AHJName.Value': 'AHJName',
        'AHJLevelCode.Value': '050',
        'BuildingCode.Value': '2021IBC',
        'BuildingCodeNotes.Value': 'BuildingCodeNotes',
        'Description.Value': 'Description',
        'DocumentSubmissionMethodNotes.Value': 'DocumentSubmissionMethodNotes',
        'ElectricCode.Value': '2020NEC',
        'ElectricCodeNotes.Value': 'ElectricCodeNotes',
        'EstimatedTurnaroundDays.Value': 0,
        'FileFolderURL.Value': 'FileFolderURL',
        'FireCode.Value': '2021IFC',
        'FireCodeNotes.Value': 'FireCodeNotes',
        'PermitIssueMethodNotes.Value': 'PermitIssueMethodNotes',
        'ResidentialCode.Value': '2021IRC',
        'ResidentialCodeNotes.Value': 'ResidentialCodeNotes',
        'URL.Value': 'URL',
        'WindCode.Value': 'ASCE716',
        'WindCodeNotes.Value': 'WindCodeNotes',
        'Address.AddrLine1.Value': 'AddrLine1',
        'Address.AddrLine2.Value': 'AddrLine2',
        'Address.AddrLine3.Value': 'AddrLine3',
        'Address.AddressType.Value': 'Mailing',
        'Address.City.Value': 'City',
        'Address.Country.Value': 'Country',
        'Address.County.Value': 'County',
        'Address.Description.Value': 'Description',
        'Address.StateProvince.Value': 'StateProvince',
        'Address.ZipPostalCode.Value': 'ZipPostalCode',
        'Address.Location.Altitude.Value': 0,
        'Address.Location.Description.Value': 'Description',
        'Address.Location.Elevation.Value': 0,
        'Address.Location.Latitude.Value': 0,
        'Address.Location.LocationDeterminationMethod.Value': 'GPS',
        'Address.Location.LocationType.Value': 'GeneralProximity',
        'Address.Location.Longitude.Value': 0,
        'Contacts[0].ContactType.Value': 'Homeowner',
        'Contacts[0].ContactTimezone.Value': 'ContactTimezone',
        'Contacts[0].Description.Value': 'Description',
        'Contacts[0].Email.Value': 'Email',
        'Contacts[0].FirstName.Value': 'FirstName',
        'Contacts[0].HomePhone.Value': 'HomePhone',
        'Contacts[0].LastName.Value': 'LastName',
        'Contacts[0].MiddleName.Value': 'MiddleName',
        'Contacts[0].MobilePhone.Value': 'MobilePhone',
        'Contacts[0].WorkPhone.Value': 'WorkPhone',
        'Contacts[0].Title.Value': 'Title',
        'Contacts[0].PreferredContactMethod.Value': 'PreferredContactMethod',
        'Contacts[0].URL.Value': 'URL',
        'DocumentSubmissionMethods[0].Value': 'SolarAPP',
        'PermitIssueMethods[0].Value': 'SolarAPP',
        'EngineeringReviewRequirements[0].RequirementLevel.Value': 'Required',
        'EngineeringReviewRequirements[0].RequirementNotes.Value': 'RequirementNotes',
        'EngineeringReviewRequirements[0].StampType.Value': 'Wet',
        'EngineeringReviewRequirements[0].Description.Value': 'Description',
        'EngineeringReviewRequirements[0].EngineeringReviewType.Value': 'StructuralEngineer'
    }
    for k, v in custom_values_dict.items():
        ahj_csv_dict[k] = v
    return ahj_csv_dict


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


@pytest.fixture
@pytest.mark.django_db
def add_enum_values():
    """
    Adds all enum values to their enum tables.
    """
    for field in ENUM_FIELDS:
        model = apps.get_model('ahj_app', field)
        model.objects.all().delete()
        model.objects.bulk_create([model(Value=choice[0]) for choice in model._meta.get_field('Value').choices])


@pytest.mark.parametrize(
    'ahj_csv_row, expected_output', [
        # Keep valid code years
        (csv_ahj_row_dict({'BuildingCode.Value': '2021IBC'}), csv_ahj_row_dict({'BuildingCode.Value': '2021IBC'})),
        (csv_ahj_row_dict({'ElectricCode.Value': '2020NEC'}), csv_ahj_row_dict({'ElectricCode.Value': '2020NEC'})),
        (csv_ahj_row_dict({'FireCode.Value': '2021IFC'}), csv_ahj_row_dict({'FireCode.Value': '2021IFC'})),
        (csv_ahj_row_dict({'ResidentialCode.Value': '2021IRC'}), csv_ahj_row_dict({'ResidentialCode.Value': '2021IRC'})),
        (csv_ahj_row_dict({'WindCode.Value': 'ASCE716'}), csv_ahj_row_dict({'WindCode.Value': 'ASCE716'})),
        # Clear invalid code years
        (csv_ahj_row_dict({'BuildingCode.Value': 'invalid_year'}), csv_ahj_row_dict({'BuildingCode.Value': ''})),
        (csv_ahj_row_dict({'ElectricCode.Value': 'invalid_year'}), csv_ahj_row_dict({'ElectricCode.Value': ''})),
        (csv_ahj_row_dict({'FireCode.Value': 'invalid_year'}), csv_ahj_row_dict({'FireCode.Value': ''})),
        (csv_ahj_row_dict({'ResidentialCode.Value': 'invalid_year'}), csv_ahj_row_dict({'ResidentialCode.Value': ''})),
        (csv_ahj_row_dict({'WindCode.Value': 'invalid_year'}), csv_ahj_row_dict({'WindCode.Value': ''}))
    ]
)
@pytest.mark.django_db
def test_remove_non_orange_button_code_years(ahj_csv_row, expected_output, add_enum_values):
    usf.remove_non_orange_button_code_years(ahj_csv_row)
    assert ahj_csv_row == expected_output


@pytest.mark.parametrize(
    'ahj_csv_row, expected_output', [
        # Keep the title
        (csv_ahj_row_dict({'Contacts[0].Title.Value': 'correct_title',
                           'Contacts[0].PreferredContactMethod.Value': ''}),
         csv_ahj_row_dict({'Contacts[0].Title.Value': 'correct_title',
                           'Contacts[0].PreferredContactMethod.Value': ''})),
        # Stop combining if valid PreferredContactMethod
        (csv_ahj_row_dict({'Contacts[0].Title.Value': 'title1',
                           'Contacts[0].PreferredContactMethod.Value': 'Email'}),
         csv_ahj_row_dict({'Contacts[0].Title.Value': 'title1',
                           'Contacts[0].PreferredContactMethod.Value': 'Email'})),
        # Stop combining if valid URL
        (csv_ahj_row_dict({'Contacts[0].Title.Value': 'title1',
                           'Contacts[0].PreferredContactMethod.Value': 'Email',
                           'Contacts[0].URL.Value': 'django.org'}),
         csv_ahj_row_dict({'Contacts[0].Title.Value': 'title1',
                           'Contacts[0].PreferredContactMethod.Value': 'Email',
                           'Contacts[0].URL.Value': 'django.org'})),
        # Stop combining if valid DocumentSubmissionMethod (SolarAPP)
        (csv_ahj_row_dict({'Contacts[0].Title.Value': 'title1',
                           'Contacts[0].PreferredContactMethod.Value': 'title2',
                           'Contacts[0].URL.Value': 'title3',
                           'PermitIssueMethods[0].Value': 'title5'}),
         csv_ahj_row_dict({'Contacts[0].Title.Value': 'title1, title2, title3',
                           'Contacts[0].PreferredContactMethod.Value': '',
                           'Contacts[0].URL.Value': '',
                           'PermitIssueMethods[0].Value': 'title5'})),
        # Stop combining if valid PermitIssueMethod (SolarAPP)
        (csv_ahj_row_dict({'Contacts[0].Title.Value': 'title1',
                           'Contacts[0].PreferredContactMethod.Value': 'title2',
                           'Contacts[0].URL.Value': 'title3',
                           'DocumentSubmissionMethods[0].Value': 'title4'}),
         csv_ahj_row_dict({'Contacts[0].Title.Value': 'title1, title2, title3, title4',
                           'Contacts[0].PreferredContactMethod.Value': '',
                           'Contacts[0].URL.Value': '',
                           'DocumentSubmissionMethods[0].Value': ''})),
        # Stop combining if reaches empty string
        (csv_ahj_row_dict({'Contacts[0].Title.Value': 'title1',
                           'Contacts[0].PreferredContactMethod.Value': 'title2',
                           'Contacts[0].URL.Value': '',
                           'DocumentSubmissionMethods[0].Value': 'title4'}),
         csv_ahj_row_dict({'Contacts[0].Title.Value': 'title1, title2',
                           'Contacts[0].PreferredContactMethod.Value': '',
                           'Contacts[0].URL.Value': '',
                           'DocumentSubmissionMethods[0].Value': 'title4'})),
        # Combine the titles
        (csv_ahj_row_dict({'Contacts[0].Title.Value': 'title1',
                           'Contacts[0].PreferredContactMethod.Value': 'title2',
                           'Contacts[0].URL.Value': 'title3',
                           'DocumentSubmissionMethods[0].Value': 'title4',
                           'PermitIssueMethods[0].Value': 'title5'}),
         csv_ahj_row_dict({'Contacts[0].Title.Value': 'title1, title2, title3, title4, title5',
                           'Contacts[0].PreferredContactMethod.Value': '',
                           'Contacts[0].URL.Value': '',
                           'DocumentSubmissionMethods[0].Value': '',
                           'PermitIssueMethods[0].Value': ''})),
        # Do nothing if multiple contacts
        (csv_ahj_row_dict({'Contacts[0].Title.Value': 'title1',
                           'Contacts[0].PreferredContactMethod.Value': 'title2',
                           'Contacts[1].Title.Value': 'title1',
                           'Contacts[1].PreferredContactMethod.Value': 'title2'}),
         csv_ahj_row_dict({'Contacts[0].Title.Value': 'title1',
                           'Contacts[0].PreferredContactMethod.Value': 'title2',
                           'Contacts[1].Title.Value': 'title1',
                           'Contacts[1].PreferredContactMethod.Value': 'title2'}))
    ]
)
@pytest.mark.django_db
def test_contact_title_field_from_csv_bug(ahj_csv_row, expected_output, add_enum_values):
    usf.fix_contact_title_field_from_csv_bug(ahj_csv_row)
    assert ahj_csv_row == expected_output
