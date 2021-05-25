from django.urls import reverse
from ahj_app.models import User, Edit, Comment
from fixtures import *
import pytest
import datetime

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
    url = reverse('edit-addition')
    response = client.post(url, {'SourceTable': 'AHJ', 'AHJPK': ahj_obj.AHJPK, 'ParentTable': 'AHJ', 'ParentID': '1'})
    print(response.data)

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