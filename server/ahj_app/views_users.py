import json
import os

from djoser.conf import settings as djoser_settings
from djoser.compat import get_user_email
from django.utils.timezone import now
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings

from .authentication import WebpageTokenAuth
from .models import AHJUserMaintains, AHJ, User, APIToken, Contact, WebpageToken, PreferredContactMethod, SunspecAllianceMemberDomain, AHJOfficeDomain
from .serializers import UserSerializer, ContactSerializer
from djoser.views import UserViewSet, TokenCreateView, TokenDestroyView
from djoser import signals
from djoser import utils
from djoser.compat import get_user_email
from djoser.conf import settings

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

@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
class ActivateUser(UserViewSet):

    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        maintainedAHJ = self.get_maintained_ahj(user.Email)
        if (maintainedAHJ):
            AHJUserMaintains.objects.create(AHJPK=maintainedAHJ, UserID=user, MaintainerStatus=1)
        user.is_active = True
        user.MemberID = self.get_member_id(user.Email)
        print(user.MemberID)
        user.save()

        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )

        if settings.SEND_CONFIRMATION_EMAIL:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.confirmation(self.request, context).send(to)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # Returns the sunspec alliance member id if domain matches a registered member. Returns None otherwise.
    def get_member_id(self, email):
        domain = SunspecAllianceMemberDomain.objects.filter(Domain=email[email.index('@') + 1 : ])
        return domain[0].MemberID if domain.exists() else None
    
    # Returns the AHJ that corresponds to the domain of the user's email. Returns None if no AHJ matches.
    def get_maintained_ahj(self, email):
        domain = AHJOfficeDomain.objects.filter(Domain=email[email.index('@') + 1 : ]).first()
        return AHJ.objects.filter(AHJID=domain.AHJID.AHJID).first() if domain else None

@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
class ConfirmPasswordReset(UserViewSet):

    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.set_password(serializer.data["new_password"])
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
        serializer.user.is_active = True # The purpose of overwriting this endpoint is to set users as active if performing password reset confirm.
        serializer.user.save()           # The user had to access their email account to perform a password reset.

        if djoser_settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": serializer.user}
            to = [get_user_email(serializer.user)]
            djoser_settings.EMAIL.password_changed_confirmation(self.request, context).send(to)
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def get_active_user(request):
    """
    Endpoint for getting the active user
    through the authtoken
    """
    # Get authtoken from request header
    authtoken = request.META.get('HTTP_AUTHORIZATION').replace('Token ', '')
    token = WebpageToken.objects.get(key=authtoken)
    user = User.objects.get(UserID=token.user_id)
    payload = UserSerializer(user, context={'fields_to_drop': []})
    return Response(payload.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def get_single_user(request, username):
    """
    Function view for getting a single user with the specified Username = username
    """
    try:
        queryset = User.objects.get(Username=username)
        payload = UserSerializer(queryset, context={'fields_to_drop': []})
        return Response(payload.data, status=status.HTTP_200_OK)
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
        token = request.META.get('HTTP_AUTHORIZATION').replace('Token ', '')
        receivedToken = WebpageToken.objects.get(key=token)
        # Check if the user requesting the user update is updating their own account
        if (receivedToken.user.UserID != user.UserID):
            raise Exception("Provided token credentials do not match user being updated.")
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
