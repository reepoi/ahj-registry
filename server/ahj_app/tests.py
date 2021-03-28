from rest_framework import status
from rest_framework.test import APITestCase
from .models import *
import json

USER_EMAIL = 'user@user.user'
USER_PASSWORD = 'userp@$$w0rd'
ENDPOINT_BASE = '/api/'
ENDPOINT_LOGIN = ENDPOINT_BASE + 'auth/token/login/'
ENDPOINT_APITOKEN_CREATE = ENDPOINT_BASE + 'auth/api-token/create/'
ENDPOINT_AHJLIST = ENDPOINT_BASE + 'ahj/'


def make_post(client, endpoint, data):
    return client.post(endpoint, data, format='json', HTTP_ACCEPT='application/json')


def setUpTestCase(testCase):
    testCase.user = User.objects.create_user(Email=USER_EMAIL, password=USER_PASSWORD)
    testCase.user.is_active = True
    testCase.user.save()


def web_login_user(testCase):
    login_response = make_post(testCase.client, ENDPOINT_LOGIN, {'Email': USER_EMAIL, 'password': USER_PASSWORD})
    webpage_token = login_response.json()['auth_token']
    set_client_credentials(testCase, webpage_token)


def set_client_credentials(testCase, token):
    testCase.client.credentials(HTTP_AUTHORIZATION='Token ' + token)


class UserTestCases(APITestCase):
    def setUp(self):
        setUpTestCase(self)

    def test_create_api_token(self):
        web_login_user(self)

        response = self.client.get(ENDPOINT_APITOKEN_CREATE)

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)

        api_token = response.json()['auth_token']
        set_client_credentials(self, api_token)
        ahjlist_response = self.client.post(ENDPOINT_AHJLIST, {})

        self.assertTrue(ahjlist_response.status_code == status.HTTP_200_OK)

    def test_replace_existing_api_token(self):
        web_login_user(self)
        self.client.get(ENDPOINT_APITOKEN_CREATE)
        response = self.client.get(ENDPOINT_APITOKEN_CREATE)

        self.assertTrue(response.status_code == status.HTTP_201_CREATED)

        # Make sure user has only one api token at a time
        self.assertTrue(APIToken.objects.filter(user=self.user).count() == 1)

        api_token = response.json()['auth_token']
        set_client_credentials(self, api_token)
        ahjlist_response = self.client.post(ENDPOINT_AHJLIST, {})

        self.assertTrue(ahjlist_response.status_code == status.HTTP_200_OK)


class WebpageAHJListTestCases(APITestCase):
    pass
