import json

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from .authentication import WebpageTokenAuth
from .models import AHJUserMaintains, AHJ, User, APIToken, Contact, PreferredContactMethod
from .serializers import UserSerializer
from djoser.views import UserViewSet, TokenCreateView, TokenDestroyView


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
def get_single_user(request, username):
    """
    Function view for getting a single user with the specified UserID = id
    """
    try:
        queryset = User.objects.get(Username=username)
        serializer = UserSerializer
        permissions = None
        context = {'fields_to_drop': []}
        payload = serializer(queryset, context=context)
        return Response(payload.data)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def user_update(request, username):
    """
    Update the user profile associated with `username` with all of the
    { Key : Value } pairs send in the POST data.
    """
    changeableFields = ['Username', 'FirstName', 'LastName', 'PersonalBio', 'URL', 'CompanyAffiliation', 'WorkPhone', 'PreferredContactMethod', 'Title']
    try:
        user = User.objects.get(Username=username)
        contact = user.ContactID
        # request.data is an immutable QueryDict, so we must make a copy
        data = request.data.copy()
        with transaction.atomic():
            for (key, value) in data.items():
                if key in changeableFields:
                    if key == 'PreferredContactMethod': # We must update enum fields seperately
                        contactMethodID = PreferredContactMethod.objects.get(Value=value) # Find the matching preferredContactMethodID
                        setattr(contact, 'PreferredContactMethod', contactMethodID)
                    else:
                        setattr(user, key, value)
                        setattr(contact, key, value)
                else:
                    raise Exception("The "+ key +" field cannot be changed.")
            user.save()
            contact.save()
        return Response('Success', status=status.HTTP_200_OK)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def create_api_token(request):
    user = request.user
    APIToken.objects.filter(user=user).delete()
    api_token = APIToken.objects.create(user=user)
    return Response({'auth_token': api_token.key}, status=status.HTTP_201_CREATED)


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
