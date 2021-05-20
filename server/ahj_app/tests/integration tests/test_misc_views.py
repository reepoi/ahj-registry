from django.urls import reverse
from ahj_app.models import User, Edit, Comment
from fixtures import *
import pytest
import datetime

@pytest.mark.django_db
def test_form_validator__username_exists(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    url = reverse('form-validator')
    response = client.get(url, {'Username':'someone'})
    assert response.data['UsernameExists']
    assert response.status_code == 200

@pytest.mark.django_db
def test_form_validator__email_exists(generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Email='a@a.com')
    url = reverse('form-validator')
    response = client.get(url, {'Email':'a@a.com'})
    assert response.data['EmailExists']
    assert response.status_code == 200

@pytest.mark.django_db
def test_form_validator__no_params(client_with_webpage_credentials):
    url = reverse('form-validator')
    response = client_with_webpage_credentials.get(url, {})
    assert not response.data['UsernameExists'] and not response.data['EmailExists'] 
    assert response.status_code == 200

@pytest.mark.django_db
def test_user_comments__comments_exist(ahj_obj, generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    comment1 = Comment.objects.create(UserID=user, AHJPK=ahj_obj.AHJPK, CommentText='This is one comment.', ReplyingTo=None)
    comment2 = Comment.objects.create(UserID=user, AHJPK=ahj_obj.AHJPK, CommentText='This is another.', ReplyingTo=comment1.CommentID)
    url = reverse('user-comments')
    response = client.get(url, {'UserID': user.UserID})
    assert len(response.data) == 2 # 2 comments returned
    assert response.status_code == 200

@pytest.mark.django_db
def test_user_comments__user_does_not_exist(client_with_webpage_credentials):
    url = reverse('user-comments')
    response = client_with_webpage_credentials.get(url, {'UserID': 99999999})
    assert len(response.data) == 0 # no comments returned
    assert response.status_code == 200

@pytest.mark.django_db
def test_comment_submit__normal_submission(ahj_obj, client_with_webpage_credentials):
    url = reverse('comment-submit')
    response = client_with_webpage_credentials.post(url, {'CommentText': 'This is a comment.', 'AHJPK':ahj_obj.AHJPK})
    assert response.data['CommentText']['Value'] == 'This is a comment.' # check if comment object returned matches
    assert response.status_code == 200
    
@pytest.mark.django_db
def test_comment_submit__no_comment(ahj_obj, client_with_webpage_credentials):
    url = reverse('comment-submit')
    response = client_with_webpage_credentials.post(url, {'AHJPK':ahj_obj.AHJPK})
    assert response.status_code == 400

@pytest.mark.django_db
def test_user_edits__edits_exist(ahj_obj, generate_client_with_webpage_credentials):
    client = generate_client_with_webpage_credentials(Username='someone')
    user = User.objects.get(Username='someone')
    edit1 = Edit.objects.create(ChangedBy= user, AHJPK=ahj_obj.AHJPK, SourceTable='Contact', SourceColumn='Title', SourceRow='143', DateRequested=datetime.datetime.now())
    edit2 = Edit.objects.create(ChangedBy= user, AHJPK=ahj_obj.AHJPK, SourceTable='Contact', SourceColumn='Title', SourceRow='143', DateRequested=datetime.datetime.now())

    url = reverse('user-edits')
    response = client.get(url, {'UserID': user.UserID})
    assert len(response.data) == 2 # 2 edits returned
    assert response.status_code == 200   

@pytest.mark.django_db
def test_user_edits__user_does_not_exist(client_with_webpage_credentials):
    url = reverse('user-edits')
    response = client_with_webpage_credentials.get(url, {'UserID': 99999999})
    assert len(response.data) == 0 # no edits returned
    assert response.status_code == 200