from fixtures import *
from ahj_app.models import SunspecAllianceMember, SunspecAllianceMemberDomain
from django.urls import reverse
import pytest
from django.conf import settings
import random
import string


def generate_sunspec_alliance_member():
    letters = string.ascii_letters
    member = SunspecAllianceMember.objects.create(MemberName=''.join(random.choice(letters) for i in range(6)))
    domain = ''.join(random.choice(letters) for i in range(4)) + '.' + ''.join(random.choice(letters) for i in range(4))
    SunspecAllianceMemberDomain.objects.create(DomainID=1, MemberID=member, Domain=domain)
    return member.MemberID, domain

"""
    MemberRateThrottle
"""
@pytest.mark.parametrize(
   'urlName, args', [
       ('ahj-public', { 'Location': {'Longitude': { 'Value': 'hello' }, 'Latitude': { 'Value': 'hello' }}}), # pass invalid args to each so early exit
       ('ahj-geo-address', {}),
       ('ahj-geo-location', { 'Latitude': { 'V': '25' }}),
   ]
)
@pytest.mark.django_db
def test_member_rate_throttle__regular_user(urlName, args, generate_client_with_api_credentials):
    generate_sunspec_alliance_member()
    client = generate_client_with_api_credentials(Email='f@f.fewbudsj')
    url = reverse(urlName)
    settings.DEFAULT_API_THROTTLE_RATE = 5 # Test with a throttle rate that is less than actual (actual rate would take insanely long to test)
    for i in range(0, settings.DEFAULT_API_THROTTLE_RATE):
        response = client.post(url, args,format='json')
        # Check second to last run is not throttled
        if (i == settings.DEFAULT_API_THROTTLE_RATE-1):
            assert isinstance(response.data, str)
    response = client.post(url, args, format='json')
    assert response.data['detail'][0:22] == 'Request was throttled.'

@pytest.mark.parametrize(
   'urlName, args', [
       ('ahj-public', { 'Location': {'Longitude': { 'Value': 'hello' }, 'Latitude': { 'Value': 'hello' }}}), # pass invalid args to each so early exit
       ('ahj-geo-address', {}),
       ('ahj-geo-location', { 'Latitude': { 'V': '25' }}),
   ]
)
@pytest.mark.django_db
def test_member_rate_throttle__member_user(urlName, args, generate_client_with_api_credentials):
    memberID, domain = generate_sunspec_alliance_member()
    client = generate_client_with_api_credentials(Email=f'f@{domain}')
    User.objects.filter(Email=f'f@{domain}').update(MemberID = memberID)

    url = reverse(urlName)
    settings.SUNSPEC_MEMBER_API_THROTTLE_RATE = 50 # Test with a throttle rate that is less than actual (actual rate would take insanely long to test)
    for i in range(0, settings.SUNSPEC_MEMBER_API_THROTTLE_RATE):
        response = client.post(url, args, format='json')
        # Check second to last run is not throttled
        if (i == settings.SUNSPEC_MEMBER_API_THROTTLE_RATE-1):
            assert isinstance(response.data, str)
    response = client.post(url, args, format='json')
    assert response.data['detail'][0:22] == 'Request was throttled.'

@pytest.mark.django_db
def test_member_rate_throttle__members_share_throttle(generate_client_with_api_credentials):
    memberID, domain = generate_sunspec_alliance_member()
    client = generate_client_with_api_credentials(Email=f'f@{domain}')
    User.objects.filter(Email=f'f@{domain}').update(MemberID = memberID)

    url = reverse('ahj-geo-address')
    settings.SUNSPEC_MEMBER_API_THROTTLE_RATE = 50 # Test with a throttle rate that is less than actual (actual rate would take insanely long to test)
    for i in range(0, settings.SUNSPEC_MEMBER_API_THROTTLE_RATE):
        response = client.post(url, {}, format='json')
        # Check second to last run is not throttled
        if (i == settings.SUNSPEC_MEMBER_API_THROTTLE_RATE-1):
            assert isinstance(response.data, str)
    response = client.post(url, {}, format='json')
    assert response.data['detail'][0:22] == 'Request was throttled.'

    # Use same domain and memberID for another user. Both users work for same company so this user should be throttled now.
    client = generate_client_with_api_credentials(Email=f'k@{domain}')
    User.objects.filter(Email=f'k@{domain}').update(MemberID = memberID)
    response = client.post(url, {}, format='json')
    assert response.data['detail'][0:22] == 'Request was throttled.'
