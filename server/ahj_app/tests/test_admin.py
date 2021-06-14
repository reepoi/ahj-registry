from django.contrib.auth import hashers
from django.db import connection
from django.urls import reverse
from django.http import HttpRequest, QueryDict
from django.test import Client
import ahj_app.admin.actions as admin_actions
import ahj_app.admin.form as admin_form
from fixtures import *
import pytest
import datetime
import requests

from ahj_app.models import User, APIToken, AHJUserMaintains, Edit


@pytest.mark.parametrize(
    'password', [
        ('new_user_password')
    ]
)
@pytest.mark.django_db
def test_reset_password(password, create_user):
    user = create_user()
    admin_actions.reset_password(user, password)
    salt = user.password.split('$')[2]
    assert hashers.make_password(password, salt) == user.password


@pytest.mark.django_db
def test_partition_by_field_users_by_api_token(create_user, create_user_with_api_token):
    for x in range(0, 10):
        if x % 2 == 0:
            create_user()
        else:
            create_user_with_api_token()
    user_queryset = User.objects.all()
    those_with_field_value, those_without_field_value = admin_actions.partition_by_field(user_queryset, 'api_token', None)
    assert None in those_with_field_value.values_list('api_token', flat=True)
    assert None not in those_without_field_value.values_list('api_token', flat=True)


@pytest.mark.parametrize(
    'form_value, expected_output', [
        ('On', True),
        ('Off', False),
        ('DoNothing', None)
    ]
)
def test_set_toggle(form_value, expected_output):
    assert admin_actions.set_toggle(form_value) == expected_output


@pytest.mark.parametrize(
    'form_value, expected_output', [
        ('on', True),
        ('off', False),
        ('other_value', False)
    ]
)
def test_set_delete(form_value, expected_output):
    assert admin_actions.set_delete(form_value) == expected_output


@pytest.mark.parametrize(
    'delete', [
        True,
        False,
        None
    ]
)
@pytest.mark.django_db
def test_delete_toggle_api_token_is_deleted(delete, create_user_with_api_token):
    user = create_user_with_api_token()
    admin_actions.delete_toggle_api_token(user, delete=delete)
    assert APIToken.objects.filter(user=user).exists() != (delete if delete is not None else False)


@pytest.mark.parametrize(
    'toggle', [
        True,
        False,
        None
    ]
)
@pytest.mark.django_db
def test_delete_toggle_api_token_is_toggled(toggle, create_user_with_api_token):
    user = create_user_with_api_token()
    admin_actions.delete_toggle_api_token(user, toggle=toggle)
    assert APIToken.objects.get(user=user).is_active == (toggle if toggle is not None else True)


@pytest.mark.django_db
def test_delete_toggle_api_token_user_has_no_api_token(create_user):
    user = create_user()
    if hasattr(user, 'api_token'):
        user.api_token.delete()
    admin_actions.delete_toggle_api_token(user, toggle=True, delete=False)
    assert not APIToken.objects.filter(user=user).exists()


def dict_make_query_dict(given_dict):
    qd = QueryDict('', mutable=True)
    qd.update(given_dict)
    return qd


@pytest.mark.parametrize(
    'expect_toggle, expect_delete', [
        (None, None),
        (None, True),
        (None, False),
        (True, None),
        (True, True),
        (True, False),
        (False, None),
        (False, True),
        (False, False)
    ]
)
@pytest.mark.django_db
def test_process_delete_toggle_api_token_data(expect_toggle, expect_delete, create_user):
    if expect_toggle:
        toggle_text = 'On'
    elif expect_toggle is False:
        toggle_text = 'Off'
    else:
        toggle_text = 'DoNothing'
    if expect_delete:
        delete_text = 'on'
    else:
        delete_text = ''
    users = []
    form_prefix = 'form-{0}'
    post_data_dict = {}
    post_query_dict = dict_make_query_dict(post_data_dict)
    for x in range(5):
        user = create_user()
        users.append(user)
        post_query_dict.update({'user_to_form': f'{user.UserID}.{form_prefix.format(x)}',
                                f'{form_prefix.format(x)}-toggle': toggle_text,
                                f'{form_prefix.format(x)}-delete_token': delete_text})
    results = admin_actions.process_delete_toggle_api_token_data(post_query_dict)
    for x in range(len(users)):
        assert results[x]['user'].UserID == users[x].UserID
        assert results[x]['toggle'] == expect_toggle
        assert results[x]['delete'] == (expect_delete if expect_delete is not None else False)


@pytest.mark.parametrize(
    'num_existing, num_kept, num_new', [
        # Remove all
        (3, 0, 0),
        # Keep all
        (3, 3, 0),
        # Add all new
        (0, 0, 3),
        # Remove one
        (3, 2, 0),
        # Remove one, add new one
        (3, 2, 1),
        # Add one
        (2, 2, 1)
    ]
)
@pytest.mark.django_db
def test_assign_ahj_official_status(num_existing, num_kept, num_new, ahj_obj_factory, create_user):
    """
    num_existing: number of AHJs a user is an AHJ Official of
    num_kept: number of AHJs a user is still an AHJ Official of
    num_new: number of AHJs a user is newly assigned as an AHJ Official of
    """
    user = create_user()
    num_existing_ahjs = []
    num_kept_ahjs = []
    num_new_ahjs = []

    # Add the starting relations for what the user is an AHJ Official of
    for x in range(num_existing):
        ahj = ahj_obj_factory()
        num_existing_ahjs.append(ahj)
        AHJUserMaintains.objects.create(UserID=user, AHJPK=ahj, MaintainerStatus=True)
    # Track what AHJs the user will should still be an AHJ Official of
    for x in range(num_kept):
        num_kept_ahjs.append(num_existing_ahjs[x])
    # Track the AHJs the user is newly assigned to be an AHJ Official of
    for x in range(num_new):
        ahj = ahj_obj_factory()
        num_new_ahjs.append(ahj)

    # Test applying the changes
    admin_form.assign_ahj_official_status(user, num_kept_ahjs + num_new_ahjs)

    assigned_ahjs = AHJUserMaintains.objects.filter(UserID=user, MaintainerStatus=True).values_list('AHJPK', flat=True)
    for ahj in num_kept_ahjs + num_new_ahjs:
        assert ahj.AHJPK in assigned_ahjs
    for ahj in (num_existing_ahjs[num_kept:] if num_kept < len(num_existing_ahjs) else []):
        assert ahj.AHJPK not in assigned_ahjs


@pytest.mark.parametrize(
    'date_str', [
        str(datetime.date.today()),
        str(datetime.date(1, 1, 1)),
        ''
    ]
)
@pytest.mark.django_db
def test_set_date_from_str(date_str):
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        date = None
    result = admin_actions.set_date_from_str(date_str)
    assert result == date


@pytest.mark.parametrize(
    'date_effective', [
        datetime.date.today(),
        datetime.date(1, 1, 1),
    ]
)
@pytest.mark.django_db
def test_process_approve_edits_data(date_effective, create_user, ahj_obj):
    form_prefix = 'form-{0}'
    post_data_dict = {}
    post_query_dict = dict_make_query_dict(post_data_dict)
    edits = []
    approving_user = create_user()
    for x in range(5):
        user = create_user()
        edit = Edit.objects.create(AHJPK=ahj_obj, ChangedBy=user, EditType='A', SourceTable='AHJ',
                                   SourceColumn='BuildingCode', SourceRow=ahj_obj.pk,
                                   DateRequested=datetime.date.today())
        edits.append(edit)
        post_query_dict.update({'edit_to_form': f'{edit.EditID}.{form_prefix.format(x)}',
                                f'{form_prefix.format(x)}-date_effective': str(date_effective)})
    results = admin_actions.process_approve_edits_data(post_query_dict, approving_user)
    for x in range(len(edits)):
        assert results[x]['edit'].EditID == edits[x].EditID
        assert results[x]['approved_by'].UserID == approving_user.UserID
        assert results[x]['date_effective'] == date_effective
        assert results[x]['apply_now'] == (date_effective == datetime.date.today())


@pytest.mark.parametrize(
    'date_effective', [
        '',
        None
    ]
)
@pytest.mark.django_db
def test_process_approve_edits_data_invalid_date_effective(date_effective, create_user, ahj_obj):
    form_prefix = 'form-{0}'
    post_data_dict = {}
    post_query_dict = dict_make_query_dict(post_data_dict)
    edits = []
    approving_user = create_user()
    for x in range(5):
        user = create_user()
        edit = Edit.objects.create(AHJPK=ahj_obj, ChangedBy=user, EditType='A', SourceTable='AHJ',
                                   SourceColumn='BuildingCode', SourceRow=ahj_obj.pk,
                                   DateRequested=datetime.date.today())
        edits.append(edit)
        post_query_dict.update({'edit_to_form': f'{edit.EditID}.{form_prefix.format(x)}',
                                f'{form_prefix.format(x)}-date_effective': str(date_effective)})
    results = admin_actions.process_approve_edits_data(post_query_dict, approving_user)
    assert len(results) == 0

# Test setting date effective to the past does not work
