from django.urls import reverse
from ahj_app.models import User, Edit, Comment, AHJInspection
from fixtures import *
from ahj_app.views_edits import *
import pytest
import datetime

@pytest.fixture
def user_obj(create_user):
    user = create_user(Username='someone')
    return user

@pytest.fixture
def add_edit_input():
    return {
        'SourceTable': 'AHJInspection',
        'SourceRow': 76,
        'SourceColumn': 'AHJInspectionName',
        'NewValue': 'NewName',
        'OldValue': 'Inspection1',
        'User': user,
        'EditType': 'U'
    }

@pytest.fixture
def add_edit_return_json():
    return {
        'SourceTable': 'AHJInspection',
        'SourceRow': 76,
        'SourceColumn': 'AHJInspectionName',
        'NewValue': 'NewName',
        'OldValue': 'Inspection1',
        'User': user,
        'EditType': 'U'
    }

"""@pytest.mark.django_db
def test_add_edit(create_user, add_edit_input, add_edit_return_json):
    user = create_user(Username='someone')
    edit = add_edit(edit_obj)
    for field, value in edit:
        print(field)"""

@pytest.mark.django_db
def test_edit_review__normal_use(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    Edit.objects.create(EditID=1, ChangedBy=user, EditType='A', SourceTable='AHJ', SourceColumn='BuildingCode', SourceRow='2118', DateRequested=datetime.datetime.now())
    url = reverse('edit-review')
    response = client.post(url, {'EditID':'1', 'Status': 'A'})
    changedEdit = Edit.objects.get(EditID=1)
    assert changedEdit.ReviewStatus == 'A'
    assert changedEdit.ApprovedBy == user
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    assert changedEdit.DateEffective == tomorrow
    assert response.status_code == 200

@pytest.mark.django_db
def test_edit_review__invalid_status(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    Edit.objects.create(EditID=1, ChangedBy=user, EditType='A', SourceTable='AHJ', SourceColumn='BuildingCode', SourceRow='2118', DateRequested=datetime.datetime.now())
    url = reverse('edit-review')
    response = client.post(url, {'EditID':'1', 'Status': 'Z'})
    assert response.status_code == 400

@pytest.mark.django_db
def test_edit_review__edit_does_not_exist(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    Edit.objects.create(EditID=1, ChangedBy=user, EditType='A', SourceTable='AHJ', SourceColumn='BuildingCode', SourceRow='2118', DateRequested=datetime.datetime.now())
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
    print(response.data)
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
    edit = Edit.objects.get(AHJPK=ahj_obj.AHJPK) # Got newly created edit object and set it as approved
    edit.ReviewStatus = 'A'
    edit.DateEffective = datetime.date.today()
    edit.ApprovedBy = user
    edit.save()
    apply_edits() # Now that it's approved, apply edits will apply it.
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
    Edit.objects.create(EditID=1, AHJPK=ahj_obj, ChangedBy=user, EditType='A', SourceTable='AHJ', SourceColumn='BuildingCode', SourceRow='2118', DateRequested=datetime.datetime.now())
    Edit.objects.create(EditID=2, AHJPK=ahj_obj, ChangedBy=user, EditType='A', SourceTable='AHJ', SourceColumn='BuildingCode', SourceRow='2118', DateRequested=datetime.datetime.now())

    url = reverse('edit-list')
    response = client.get(url, {'AHJPK':'1'})
    assert len(response.data) == 2

@pytest.mark.django_db
def test_edit_list__missing_param(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    
    url = reverse('edit-list')
    response = client.get(url)
    assert response.status_code == 400