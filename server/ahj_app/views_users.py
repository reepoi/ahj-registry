import json
import os

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.core.files.storage import default_storage
from django.conf import settings

from .authentication import WebpageTokenAuth
from .models import AHJUserMaintains, AHJ, User, APIToken, Contact, WebpageToken
from .serializers import UserSerializer, ContactSerializer, SubscribedChannelsSerializer
from djoser.views import UserViewSet, TokenCreateView, TokenDestroyView

import base64
from filetype import guess_extension


def user_with_img(user):
    """
    Function for appending a User Photo
    and chat rooms to the basic information given by the DB
    """
    try:  # try to get the stored image
        with default_storage.open(user.Photo, 'rb') as f:
            file_obj = f.read()
    except:  # if the filepath doesn't exist just send back the default image
        with default_storage.open(settings.DEFAULT_USER_IMG, 'rb') as f:
            file_obj = f.read()
    # encode the file using base64 for the front-end
    file_obj = base64.b64encode(file_obj)
    return {
        'UserID': user.UserID,
        'ContactID': ContactSerializer(user.ContactID).data,
        'Username': user.Username,
        'Email': user.Email,
        'PersonalBio': user.PersonalBio,
        'CompanyAffiliation': user.CompanyAffiliation,
        'Photo': file_obj,
        'IsPeerReviewer': user.IsPeerReviewer,
        'NumReviewsDone': user.NumReviewsDone,
        'AcceptedEdits': user.AcceptedEdits,
        'SubmittedEdits': user.SubmittedEdits,
        'CommunityScore': user.CommunityScore,
        'APICalls': user.APICalls,
        'SignUpDate': user.SignUpDate,
        'MaintainedAHJs': user.get_maintained_ahjs(),
        'ChatRooms': SubscribedChannelsSerializer(
            user.get_subscribed_channels(), many=True).data
    }


@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
class RegisterUser(UserViewSet):
    pass


@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
class LoginUser(TokenCreateView):
    pass

@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
class LogoutUser(TokenDestroyView):
    pass


@api_view(['GET'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def get_active_user(request):
    """
    Endpoint for getting the active user
    through the authtoken
    """
    try:
        # Get authtoken from request header
        authtoken = request.META.get('HTTP_AUTHORIZATION').replace('Token ', '')
        token = WebpageToken.objects.get(key=authtoken)
        user = User.objects.get(UserID=token.user_id)
        user = user_with_img(user)
        return Response(user, status=status.HTTP_200_OK)
    except Exception as e:
        print('ERROR GET ACTIVE USER : ', str(e))
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def get_single_user(request, username):
    """
    Function view for getting a single user with the specified UserID = id
    """
    try:
        # get the user
        user = User.objects.get(Username=username)
        # load and add the photo
        user = user_with_img(user)
        return Response(user, status=status.HTTP_200_OK)
    except Exception as e:
        print('ERROR GET SINGLE USER : ', str(e))
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def user_update(request, username):
    """
    Update the user profile associated with `username` with all of the
    { Key : Value } pairs send in the POST data.
    """
    fp = ''  # to help with error correction
    photo_obj = None
    changeableFields = ['Username', 'FirstName', 'LastName', 'PersonalBio', 'URL', 'CompanyAffiliation', 'WorkPhone', 'PreferredContactMethod', 'Title']
    try:
        user = User.objects.get(Username=username)
        token = request.META.get('HTTP_AUTHORIZATION').replace('Token ', '')
        receivedToken = WebpageToken.objects.get(key=token)
        # Check if the user requesting the user update is updating their own account
        if (receivedToken.user.UserID != user.UserID):
            raise Exception("Provided token credentials do not match user being updated.")
        contact = user.ContactID
        # request.data is an immutable QueryDict, so we must make a copy
        data = request.data.copy()
        photo_obj = data.pop('Photo', None)
        if photo_obj is not None:  # this means the photo is getting updated
            photo_obj = photo_obj[0]
            fp = settings.STORAGE_DIRS['USER_IMG'] + str(user.UserID) + '.' + guess_extension(photo_obj)
            with default_storage.open(fp, 'wb') as f:
                for chunk in photo_obj.chunks():
                    f.write(chunk)
            # write the file to the system
            data['Photo'] = fp  # the filepath needs to get updated in the db
        with transaction.atomic():
            for (key, value) in data.items():
                if key in changeableFields:
                    setattr(user, key, value)
                    setattr(contact, key, value)
                else:
                    raise Exception("The "+ key +" field cannot be changed.")
            user.save()
            contact.save()
        return Response('Success', status=status.HTTP_200_OK)
    except Exception as e:
        print('ERROR USER UPDATE : ', str(e))
        if photo_obj is not None and os.path.exists(settings.MEDIA_ROOT + fp):
            os.remove(settings.MEDIA_ROOT + fp)
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def create_api_token(request):
    try:
        user = request.user
        with transaction.atomic():
            APIToken.objects.filter(user=user).delete()
            api_token = APIToken.objects.create(user=user)
        return Response({'auth_token': api_token.key}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def set_ahj_maintainer(request):
    """
    View to assign a user as a data maintainer of an AHJ
    Expects a Username and a the primary key of an AHJ (AHJPK)
    """
    try:
        username = request.data['Username']
        ahjpk = request.data['AHJPK']
        user = User.objects.get(Username=username)
        ahj = AHJ.objects.get(AHJPK=ahjpk)
        maintainer_record = AHJUserMaintains.objects.filter(AHJPK=ahj, UserID=user)
        if maintainer_record.exists():
            maintainer_record.update(MaintainerStatus=True)
        else:
            AHJUserMaintains.objects.create(UserID=user, AHJPK=ahj, MaintainerStatus=True)
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def remove_ahj_maintainer(request):
    """
    View to revoke a user as a data maintainer of an AHJ
    Expects a user's webpage token and a the primary key of an AHJ (AHJPK)
    """
    try:
        username = request.data['Username']
        ahjpk = request.data['AHJPK']
        user = User.objects.get(Username=username)
        ahj = AHJ.objects.get(AHJPK=ahjpk)
        AHJUserMaintains.objects.filter(AHJPK=ahj, UserID=user).update(MaintainerStatus=False)
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
