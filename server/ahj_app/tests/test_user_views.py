from django.urls import reverse
from ahj_app.models import User, Contact, AHJUserMaintains, PreferredContactMethod
from fixtures import *
import pytest
from django.conf import settings

"""
    User View Endpoints
"""

@pytest.mark.django_db
def test_get_active_user(client_with_webpage_credentials):
    url = reverse('active-user-info')
    response = client_with_webpage_credentials.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_get_single_user__user_exists(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    url = reverse('single-user-info', kwargs={'username': 'someone'})
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_get_single_user__user_does_not_exist(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    url = reverse('single-user-info', kwargs={'username': 'test'})
    response = client.get(url)
    assert response.status_code == 400

@pytest.mark.django_db
def test_update_user__user_exists(generate_client_with_webpage_credentials, create_user):
    admin_user = create_user()
    admin_token = WebpageToken.objects.create(user_id=admin_user.UserID)
    settings.WEBPAGE_TOKEN_CONSTANT = admin_token.key
    PreferredContactMethod.objects.create(PreferredContactMethodID=1, Value='Email') # create a PreferredContactMethod so we can change that attr in the Contact model
    client = generate_client_with_webpage_credentials(Username='someone', Email='test@test.com')
    newUserData = {
        'Username': 'username',
        'FirstName': 'first',
        'LastName': 'last',
        'PersonalBio': 'pb',
        'URL': 'url',
        'CompanyAffiliation': 'ca',
        'WorkPhone': '123-456-7890',
        'PreferredContactMethod': 'Email',
        'Title': 'title'
    }
    # send update to user-update path 
    url = reverse('user-update', kwargs={'username': 'someone'})
    response = client.post(url, newUserData)
    print(response.data)
    # Update contact and user objects
    user = User.objects.get(Username='username')
    ContactID = user.ContactID
    # For each field in the User and Contact objects that match a field in newUserData, see if it was updated.
    for field in User._meta.get_fields():
        if field.name in newUserData:
            assert getattr(user, field.name) == newUserData[field.name]
    for field in Contact._meta.get_fields():
        if field.name in newUserData:
            if field.name == 'PreferredContactMethod':
                assert getattr(ContactID, 'PreferredContactMethod').Value == newUserData[field.name]
            else:
                assert getattr(ContactID, field.name) == newUserData[field.name]
    
    assert response.status_code == 200

@pytest.mark.django_db
def test_update_user__user_updating_another_user(create_user, client_with_webpage_credentials):
    user2 = create_user(Username='test')
    url = reverse('user-update', kwargs={'username': 'test'})
    response = client_with_webpage_credentials.post(url, {'Username': 'usernamechange'})
    assert response.status_code == 400

@pytest.mark.django_db
def test_update_user__unchangable_field_changed(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    url = reverse('user-update', kwargs={'username': 'someone'})
    response = client.post(url, {'Email': 'new@new.com'})
    assert response.status_code == 400

@pytest.mark.django_db
def test_update_user__user_does_not_exist(client_with_webpage_credentials):
    url = reverse('user-update', kwargs={'username': 'notexist'})
    response = client_with_webpage_credentials.post(url, {'Username': 'usernamechange'})
    assert response.status_code == 400

@pytest.mark.django_db
def test_create_api_token__token_does_not_exist(client_with_webpage_credentials):
    url = reverse('create-api-token')
    response = client_with_webpage_credentials.get(url)
    assert response.status_code == 201

@pytest.mark.django_db
def test_create_api_token__token_already_exist(client_with_webpage_credentials):
    url = reverse('create-api-token')
    client_with_webpage_credentials.get(url) # Create token, then call token creation view again
    response = client_with_webpage_credentials.get(url)
    assert response.status_code == 201

@pytest.mark.django_db
def test_set_ahj_maintainer__already_maintains(ahj_obj, generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')

    AHJMaintainer = AHJUserMaintains.objects.create(AHJPK=ahj_obj, UserID=user, MaintainerStatus=1)
    
    userData = {'Username': user.Username, 'AHJPK': ahj_obj.AHJPK}
    url = reverse('ahj-set-maintainer')
    response = client.post(url, userData)
    assert response.status_code == 200

@pytest.mark.django_db
def test_set_ahj_maintainer__does_not_already_maintain(ahj_obj, generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    
    userData = {'Username': user.Username, 'AHJPK': ahj_obj.AHJPK}
    url = reverse('ahj-set-maintainer')
    response = client.post(url, userData)
    assert response.status_code == 200

@pytest.mark.django_db
def test_set_ahj_maintainer__invalid_params(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    # invalid username
    userData = {'Username': 'notexist'}
    url = reverse('ahj-set-maintainer')
    response = client.post(url, userData)
    assert response.status_code == 400
    # invalid AHJPK
    userData = {'Username': 'someone', 'AHJPK': 999999999}
    url = reverse('ahj-set-maintainer')
    response = client.post(url, userData)
    assert response.status_code == 400

@pytest.mark.django_db
def test_remove_ahj_maintainer__maintainer_exists(ahj_obj, generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')

    AHJMaintainer = AHJUserMaintains.objects.create(AHJPK=ahj_obj, UserID=user, MaintainerStatus=1)
    assert AHJUserMaintains.objects.get(UserID=user.UserID).MaintainerStatus == 1 # Check before we change the status
    
    userData = {'Username': 'someone', 'AHJPK': ahj_obj.AHJPK}
    url = reverse('ahj-remove-maintainer')
    response = client.post(url, userData)
    assert AHJUserMaintains.objects.get(UserID=user.UserID).MaintainerStatus == 0
    assert response.status_code == 200

@pytest.mark.django_db
def test_remove_ahj_maintainer__maintainer_does_not_exist(ahj_obj, generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    
    userData = {'Username': 'someone', 'AHJPK': ahj_obj.AHJPK}
    url = reverse('ahj-remove-maintainer')
    response = client.post(url, userData)
    # If we are removing maintainer privileges from a user that already didn't have maintainer privileges, still return 200
    assert response.status_code == 200

@pytest.mark.django_db
def test_remove_ahj_maintainer__invalid_params(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    # invalid username
    userData = {'Username': 'notexist'}
    url = reverse('ahj-remove-maintainer')
    response = client.post(url, userData)
    assert response.status_code == 400
    # invalid AHJPK
    userData = {'Username': 'someone', 'AHJPK': 999999999}
    url = reverse('ahj-remove-maintainer')
    response = client.post(url, userData)
    assert response.status_code == 400
