import uuid
from decimal import Decimal

from django.apps import apps
from ahj_app.models import User, Edit, Comment, AHJInspection, Contact, Address, Location, AHJ
from django.urls import reverse
from django.utils import timezone

import pytest
import datetime
from fixtures import create_user, ahj_obj, generate_client_with_webpage_credentials, api_client
from ahj_app.usf import ENUM_FIELDS, get_enum_value_row

from ahj_app.models_field_enums import RequirementLevel

from ahj_app import views_edits


@pytest.fixture
def user_obj(create_user):
    user = create_user(Username='someone')
    return user


@pytest.fixture
def add_enums():
    RequirementLevel.objects.create(Value='ConditionallyRequired')
    RequirementLevel.objects.create(Value='Required')
    RequirementLevel.objects.create(Value='Optional')


def create_obj_from_dict(model_name, obj_dict):
    for k, v in obj_dict.items():
        if type(v) is dict:
            sub_obj_model_name = v.pop('_model_name')
            obj_dict[k] = create_obj_from_dict(sub_obj_model_name, v)
    obj = apps.get_model('ahj_app', model_name).objects.create(**obj_dict)
    return obj


def set_obj_field(obj, field_name, value):
    value = get_enum_value_row(field_name, value) if field_name in ENUM_FIELDS else value
    setattr(obj, field_name, value)
    obj.save()


def filter_to_edit(edit_dict):
    edit_dict['DateRequested__date'] = edit_dict.pop('DateRequested')
    edit_dict['DateEffective__date'] = edit_dict.pop('DateEffective')
    return Edit.objects.filter(**edit_dict)


def check_edit_exists(edit_dict):
    return filter_to_edit(edit_dict).exists()


@pytest.mark.django_db
def test_edit_review__normal_use(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    Edit.objects.create(EditID=1, ChangedBy=user, EditType='A', SourceTable='AHJ', SourceColumn='BuildingCode', SourceRow='2118', DateRequested=timezone.now())
    url = reverse('edit-review')
    response = client.post(url, {'EditID':'1', 'Status': 'A'})
    assert response.status_code == 200
    changedEdit = Edit.objects.get(EditID=1)
    assert changedEdit.ReviewStatus == 'A'
    assert changedEdit.ApprovedBy == user
    tomorrow = timezone.now() + datetime.timedelta(days=1)
    assert changedEdit.DateEffective.date() == tomorrow.date()

@pytest.mark.django_db
def test_edit_review__invalid_status(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    Edit.objects.create(EditID=1, ChangedBy=user, EditType='A', SourceTable='AHJ', SourceColumn='BuildingCode', SourceRow='2118', DateRequested=timezone.now())
    url = reverse('edit-review')
    response = client.post(url, {'EditID':'1', 'Status': 'Z'})
    assert response.status_code == 400

@pytest.mark.django_db
def test_edit_review__edit_does_not_exist(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    Edit.objects.create(EditID=1, ChangedBy=user, EditType='A', SourceTable='AHJ', SourceColumn='BuildingCode', SourceRow='2118', DateRequested=timezone.now())
    url = reverse('edit-review')
    response = client.post(url, {'EditID':'100', 'Status': 'A'})
    assert response.status_code == 400

@pytest.mark.django_db
@pytest.mark.parametrize(
   'params', [
       ({}),
       ({'EditID': '1'}),
       ({'Status': 'A'}),
   ]
)
def test_edit_review__missing_param(params, generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    url = reverse('edit-review')
    response = client.post(url, params)
    assert response.status_code == 400

@pytest.mark.django_db
def test_edit_addition__normal_use(ahj_obj, generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    AHJInspection.objects.create(AHJPK=ahj_obj, AHJInspectionName='Inspection1', TechnicianRequired=1, InspectionStatus=True)
    url = reverse('edit-addition')

    response = client.post(url, {
        'SourceTable': 'AHJInspection', 
        'AHJPK': ahj_obj.AHJPK, 
        'ParentTable': 'AHJ', 
        'ParentID': ahj_obj.AHJPK, 
        'Value': [ 
            { 'AHJInspectionName': 'NewName'}
    ]}, format='json')
    assert response.status_code == 200
    assert response.data[0]['AHJInspectionName']['Value'] == 'NewName' # confirm returned AHJInspection was updated
    edit = Edit.objects.get(AHJPK=ahj_obj.AHJPK)
    assert edit.EditType == 'A'
    assert edit.NewValue == 'True'
    assert edit.SourceRow == response.data[0]['InspectionID']['Value']
    

@pytest.mark.django_db
@pytest.mark.parametrize(
   'params', [
       ({'SourceTable': 'AHJ', 'ParentID': '1', 'ParentTable': 'AHJ'}),
       ({'AHJPK': '1', 'ParentID': '1', 'ParentTable': 'AHJ'}),
       ({'SourceTable': 'AHJ', 'AHJPK': '1', 'ParentTable': 'AHJ'}),
       ({'SourceTable': 'AHJ', 'AHJPK': '1', 'ParentID': '1'})
   ]
)
def test_edit_addition__missing_param(params, generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    url = reverse('edit-addition')
    response = client.post(url, params)
    assert response.status_code == 400

@pytest.mark.django_db
def test_edit_deletion__normal_use(ahj_obj, generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    inspection = AHJInspection.objects.create(AHJPK=ahj_obj, AHJInspectionName='Inspection1', TechnicianRequired=1, InspectionStatus=True)
    url = reverse('edit-deletion')

    response = client.post(url, {
        'SourceTable': 'AHJInspection', 
        'AHJPK': ahj_obj.AHJPK, 
        'ParentTable': 'AHJ', 
        'ParentID': ahj_obj.AHJPK, 
        'Value': [ 
            inspection.InspectionID
    ]}, format='json')
    assert response.status_code == 200
    edit = Edit.objects.get(AHJPK=ahj_obj.AHJPK)
    assert edit.EditType == 'D'
    assert edit.NewValue == 'False'
    assert edit.SourceRow == response.data[0]['InspectionID']['Value']

@pytest.mark.django_db
@pytest.mark.parametrize(
   'params', [
       ({'SourceTable': 'AHJ'}),
       ({'AHJPK': '1'}),
   ]
)
def test_edit_deletion__missing_param(params, generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    url = reverse('edit-deletion')
    response = client.post(url, params)
    assert response.status_code == 400

@pytest.mark.django_db
def test_edit_update__normal_use(ahj_obj, generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    inspection = AHJInspection.objects.create(AHJPK=ahj_obj, AHJInspectionName='Inspection1', TechnicianRequired=1, InspectionStatus=True)
    url = reverse('edit-update')
    input = [
        {
            'AHJPK': ahj_obj.AHJPK,
            'SourceTable': 'AHJInspection',
            'SourceRow': inspection.pk,
            'SourceColumn': 'AHJInspectionName',
            'NewValue': 'NewName'
        }
    ]
    response = client.post(url, input, format='json')
    assert response.status_code == 200
    edit = Edit.objects.get(AHJPK=ahj_obj.AHJPK) # Got newly created edit object and set it as approved
    edit.ReviewStatus = 'A'
    edit.DateEffective = timezone.now()
    edit.ApprovedBy = user
    edit.save()
    views_edits.apply_edits() # Now that it's approved, apply edits will apply it.
    Inspection = AHJInspection.objects.get(AHJPK=ahj_obj)
    assert Inspection.AHJInspectionName == 'NewName'

@pytest.mark.django_db
@pytest.mark.parametrize(
   'params', [
       ({'SourceTable': 'AHJ'}),
       ({'AHJPK': '1', 'SourceTable': 'AHJ', 'SourceRow': 'row', 'SourceColumn': 'column'}),
   ]
)
def test_edit_update__missing_param(params, generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    url = reverse('edit-deletion')
    response = client.post(url, params)
    assert response.status_code == 400

@pytest.mark.django_db
def test_edit_list__normal_use(ahj_obj, generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    Edit.objects.create(EditID=1, AHJPK=ahj_obj, ChangedBy=user, EditType='A', SourceTable='AHJ', SourceColumn='BuildingCode', SourceRow='2118', DateRequested=timezone.now())
    Edit.objects.create(EditID=2, AHJPK=ahj_obj, ChangedBy=user, EditType='A', SourceTable='AHJ', SourceColumn='BuildingCode', SourceRow='2118', DateRequested=timezone.now())

    url = reverse('edit-list')
    response = client.get(url, {'AHJPK':'1'})
    assert response.status_code == 200
    assert len(response.data) == 2

@pytest.mark.django_db
def test_edit_list__missing_param(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    
    url = reverse('edit-list')
    response = client.get(url)
    assert response.status_code == 400


@pytest.mark.django_db
def test_edit_addition__applied_immediately(ahj_obj, generate_client_with_webpage_credentials):
    """
    This tests that edits are applied to what they are editing immediately.
    It is temporary functionality to be removed after the 2.0 release.
    """
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    url = reverse('edit-addition')

    response = client.post(url, {'SourceTable': 'Contact',
                                 'AHJPK': ahj_obj.AHJPK,
                                 'ParentTable': 'AHJ',
                                 'ParentID': ahj_obj.AHJPK,
                                 'Value': [{}]}, format='json')
    assert response.status_code == 200
    contact_id = response.data[0]['ContactID']['Value']
    assert Contact.objects.filter(ContactID=contact_id).exists()
    assert Edit.objects.get(AHJPK=ahj_obj.AHJPK).ReviewStatus == 'A'


@pytest.mark.django_db
def test_edit_update__applied_immediately(ahj_obj, generate_client_with_webpage_credentials):
    """
    This tests that edits are applied to what they are editing immediately.
    It is temporary functionality to be removed after the 2.0 release.
    """
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    url = reverse('edit-update')

    contact = Contact.objects.create(ParentTable='AHJ', ParentID=ahj_obj.AHJPK)
    response = client.post(url, [{'SourceTable': 'Contact',
                                 'SourceRow': contact.ContactID,
                                 'SourceColumn': 'FirstName',
                                 'NewValue': 'NewName',
                                 'AHJPK': ahj_obj.AHJPK}], format='json')
    assert response.status_code == 200
    assert Contact.objects.get(ContactID=contact.ContactID).FirstName == 'NewName'
    assert Edit.objects.get(AHJPK=ahj_obj.AHJPK).ReviewStatus == 'A'


@pytest.mark.parametrize(
    'model_name, obj_dict, field_name, old_value, new_value', [
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'AHJName', 'oldname', 'newname'),
        ('Contact', {'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'FirstName', 'oldname', 'newname'),
        ('Address', {'LocationID': {'_model_name': 'Location'}}, 'Country', 'oldcountry', 'newcountry'),
        ('Location', {}, 'Elevation', Decimal('0.00000000'), Decimal('10000.00000000')),
        ('EngineeringReviewRequirement', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}},
         'RequirementLevel', 'ConditionallyRequired', 'Required'),
        ('AHJInspection', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}},
         'FileFolderURL', 'oldurl', 'newurl'),
        ('FeeStructure', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}},
         'FeeStructureID', str(uuid.uuid4()), str(uuid.uuid4()))
    ]
)
@pytest.mark.django_db
def test_edit_revert__edit_update(model_name, obj_dict, field_name, old_value, new_value, create_user, ahj_obj, add_enums):
    user = create_user()
    obj = create_obj_from_dict(model_name, obj_dict)
    set_obj_field(obj, field_name, new_value)
    edit_dict = {'ChangedBy': user, 'ApprovedBy': user,
                 'SourceTable': model_name, 'SourceRow': obj.pk, 'SourceColumn': field_name,
                 'OldValue': old_value, 'NewValue': new_value,
                 'DateRequested': timezone.now(), 'DateEffective': timezone.now(),
                 'ReviewStatus': 'A', 'EditType': 'U', 'AHJPK': ahj_obj}
    edit = Edit.objects.create(**edit_dict)
    views_edits.revert_edit(user, edit)
    edit_dict['OldValue'], edit_dict['NewValue'] = edit.NewValue, edit.OldValue
    assert getattr(obj._meta.model.objects.get(**{obj._meta.pk.name: obj.pk}), field_name) == (get_enum_value_row(field_name, old_value) if field_name in ENUM_FIELDS else old_value)
    assert check_edit_exists(edit_dict) is True


@pytest.mark.django_db
def test_edit_revert__revert_edit_old_value_uses_current_row_value(create_user, ahj_obj):
    user = create_user()
    old_value = 'oldname'
    middle_value = 'newername'
    new_value = 'newestname'
    edit_dict = {'ChangedBy': user, 'ApprovedBy': user,
                 'SourceTable': 'AHJ', 'SourceRow': ahj_obj.pk, 'SourceColumn': 'AHJName',
                 'OldValue': old_value, 'NewValue': middle_value,
                 'DateRequested': timezone.now(), 'DateEffective': timezone.now(),
                 'ReviewStatus': 'A', 'EditType': 'U', 'AHJPK': ahj_obj}
    edit = Edit.objects.create(**edit_dict)
    edit_dict['OldValue'], edit_dict['NewValue'] = edit_dict['NewValue'], new_value
    setattr(ahj_obj, 'AHJName', new_value)
    ahj_obj.save()
    newer_edit = Edit.objects.create(**edit_dict)
    views_edits.revert_edit(user, edit)
    edit_dict['OldValue'], edit_dict['NewValue'] = edit_dict['NewValue'], old_value
    reverting_edit = filter_to_edit(edit_dict)
    assert reverting_edit.exists() is True
    assert reverting_edit.first().OldValue == new_value
    assert AHJ.objects.get(AHJPK=ahj_obj.pk).AHJName == old_value


@pytest.mark.parametrize(
    'parent_model_name, parent_obj_dict, model_name, obj_dict', [
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'Contact', {'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}),
        ('AHJInspection', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}},
         'Contact', {'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}),
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'EngineeringReviewRequirement', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}}),
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'AHJInspection', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}}),
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'DocumentSubmissionMethod', {'Value': 'SolarApp'}),
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'PermitIssueMethod', {'Value': 'SolarApp'}),
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'FeeStructure', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}})
    ]
)
@pytest.mark.django_db
def test_edit_revert__edit_addition(parent_model_name, parent_obj_dict, model_name, obj_dict, create_user, ahj_obj):
    user = create_user()
    parent_obj = create_obj_from_dict(parent_model_name, parent_obj_dict)
    obj = create_obj_from_dict(model_name, obj_dict)
    relation = obj.create_relation_to(parent_obj)
    set_obj_field(relation, relation.get_relation_status_field(), True)
    edit_dict = {'ChangedBy': user, 'ApprovedBy': user,
                 'SourceTable': relation.__class__.__name__, 'SourceRow': relation.pk, 'SourceColumn': relation.get_relation_status_field(),
                 'OldValue': None, 'NewValue': True,
                 'DateRequested': timezone.now(), 'DateEffective': timezone.now(),
                 'ReviewStatus': 'A', 'EditType': 'A', 'AHJPK': ahj_obj}
    edit = Edit.objects.create(**edit_dict)
    views_edits.revert_edit(user, edit)
    edit_dict['OldValue'], edit_dict['NewValue'] = edit_dict['NewValue'], False
    assert check_edit_exists(edit_dict) is True
    assert getattr(relation._meta.model.objects.get(**{relation._meta.pk.name: relation.pk}), relation.get_relation_status_field()) is edit_dict['NewValue']


@pytest.mark.parametrize(
    'parent_model_name, parent_obj_dict, model_name, obj_dict', [
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'Contact', {'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}),
        ('AHJInspection', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}},
         'Contact', {'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}),
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'EngineeringReviewRequirement', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}}),
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'AHJInspection', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}}),
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'DocumentSubmissionMethod', {'Value': 'SolarApp'}),
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'PermitIssueMethod', {'Value': 'SolarApp'}),
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'FeeStructure', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}})
    ]
)
@pytest.mark.django_db
def test_edit_revert__edit_deletion(parent_model_name, parent_obj_dict, model_name, obj_dict, create_user, ahj_obj):
    user = create_user()
    parent_obj = create_obj_from_dict(parent_model_name, parent_obj_dict)
    obj = create_obj_from_dict(model_name, obj_dict)
    relation = obj.create_relation_to(parent_obj)
    set_obj_field(relation, relation.get_relation_status_field(), False)
    edit_dict = {'ChangedBy': user, 'ApprovedBy': user,
                 'SourceTable': relation.__class__.__name__, 'SourceRow': relation.pk, 'SourceColumn': relation.get_relation_status_field(),
                 'OldValue': True, 'NewValue': False,
                 'DateRequested': timezone.now(), 'DateEffective': timezone.now(),
                 'ReviewStatus': 'A', 'EditType': 'D', 'AHJPK': ahj_obj}
    edit = Edit.objects.create(**edit_dict)
    views_edits.revert_edit(user, edit)
    edit_dict['OldValue'], edit_dict['NewValue'] = edit_dict['NewValue'], edit_dict['OldValue']
    assert check_edit_exists(edit_dict) is True
    assert getattr(relation._meta.model.objects.get(**{relation._meta.pk.name: relation.pk}), relation.get_relation_status_field()) is edit_dict['NewValue']


@pytest.mark.parametrize(
    'date_effective1, date_effective2', [
        (timezone.make_aware(datetime.datetime(1, 1, 1)), timezone.make_aware(datetime.datetime(2, 2, 2))),
        (timezone.make_aware(datetime.datetime(2, 2, 2)), timezone.make_aware(datetime.datetime(1, 1, 1)))
    ]
)
@pytest.mark.django_db
def test_edit_is_resettable(date_effective1, date_effective2, create_user, ahj_obj):
    user = create_user()
    edit_dict = {'ChangedBy': user, 'ApprovedBy': user,
                 'SourceTable': 'AHJ', 'SourceRow': ahj_obj.pk, 'SourceColumn': 'AHJName',
                 'OldValue': 'oldname', 'NewValue': 'newername',
                 'DateRequested': date_effective1, 'DateEffective': date_effective1,
                 'ReviewStatus': 'A', 'EditType': 'U', 'AHJPK': ahj_obj}
    edit1 = Edit.objects.create(**edit_dict)
    edit_dict['DateRequested'], edit_dict['DateEffective'] = date_effective2, date_effective2
    edit2 = Edit.objects.create(**edit_dict)
    is_resettable = views_edits.edit_is_resettable(edit1)
    assert is_resettable == (date_effective1 > date_effective2)


@pytest.mark.parametrize(
    'model_name, obj_dict, field_name, old_value, new_value, make_later_edit', [
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'AHJName', 'oldname', 'newname', True),
        ('Contact', {'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'FirstName', 'oldname', 'newname', True),
        ('Address', {'LocationID': {'_model_name': 'Location'}}, 'Country', 'oldcountry', 'newcountry', True),
        ('Location', {}, 'Elevation', 0, 10000, True),
        ('EngineeringReviewRequirement', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}},
         'RequirementLevel', 'ConditionallyRequired', 'Required', True),
        ('AHJInspection', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}},
         'FileFolderURL', 'oldurl', 'newurl', True),
        ('FeeStructure', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}},
         'FeeStructureID', str(uuid.uuid4()), str(uuid.uuid4()), True),
        ('AHJ', {'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'AHJName', 'oldname', 'newname', False),
        ('Contact', {'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}},
         'FirstName', 'oldname', 'newname', False),
        ('Address', {'LocationID': {'_model_name': 'Location'}}, 'Country', 'oldcountry', 'newcountry', False),
        ('Location', {}, 'Elevation', Decimal('0.00000000'), Decimal('10000.00000000'), False),
        ('EngineeringReviewRequirement', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}},
         'RequirementLevel', 'ConditionallyRequired', 'Required', False),
        ('AHJInspection', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}},
         'FileFolderURL', 'oldurl', 'newurl', False),
        ('FeeStructure', {'AHJPK': {'_model_name': 'AHJ', 'AHJID': uuid.uuid4(), 'AddressID': {'_model_name': 'Address', 'LocationID': {'_model_name': 'Location'}}}},
         'FeeStructureID', str(uuid.uuid4()), str(uuid.uuid4()), False)
    ]
)
@pytest.mark.django_db
def test_edit_reset(model_name, obj_dict, field_name, old_value, new_value, create_user, ahj_obj, make_later_edit, add_enums):
    user = create_user()
    obj = create_obj_from_dict(model_name, obj_dict)
    # pdb.set_trace()
    edit_dict = {'ChangedBy': user, 'ApprovedBy': user,
                 'SourceTable': model_name, 'SourceRow': obj.pk, 'SourceColumn': field_name,
                 'OldValue': old_value, 'NewValue': new_value,
                 'DateRequested': timezone.now(), 'DateEffective': timezone.now(),
                 'ReviewStatus': 'A', 'EditType': 'U', 'AHJPK': ahj_obj}
    edit = Edit.objects.create(**edit_dict)
    edits_to_apply = [edit]
    if make_later_edit:
        if type(edit_dict['OldValue']) is int:
            edit_dict['OldValue'], edit_dict['NewValue'] = old_value + 1, new_value + 1
        elif model_name == 'FeeStructure':
            edit_dict['OldValue'], edit_dict['NewValue'] = str(uuid.uuid4()), str(uuid.uuid4())
        elif model_name == 'EngineeringReviewRequirement':
            edit_dict['OldValue'], edit_dict['NewValue'] = 'Required', 'Optional'
        else:
            edit_dict['OldValue'], edit_dict['NewValue'] = f'!{old_value[1:]}', f'!{new_value[1:]}'
        edit_dict['DateRequested'], edit_dict['DateEffective'] = edit_dict['DateRequested'] + datetime.timedelta(days=1), edit_dict['DateEffective'] + datetime.timedelta(days=1)
        later_edit = Edit.objects.create(**edit_dict)
        edits_to_apply.append(later_edit)
    # NOTE: apply_edits is tested separately above
    views_edits.apply_edits(ready_edits=edits_to_apply)
    views_edits.reset_edit(user, edit)
    if make_later_edit:
        assert check_edit_exists(edit_dict) is True
    else:
        edit = Edit.objects.get(EditID=edit.EditID)
        assert edit.ReviewStatus == 'P'
        assert edit.ApprovedBy is None
        assert edit.DateEffective is None
    assert getattr(obj._meta.model.objects.get(**{obj._meta.pk.name: obj.pk}), field_name) == (get_enum_value_row(field_name, old_value) if field_name in ENUM_FIELDS else old_value)
