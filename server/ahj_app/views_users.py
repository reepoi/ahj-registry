import json

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .authentication import WebpageTokenAuth
from .models import AHJUserMaintains, AHJ, User, APIToken
from .serializers import UserSerializer


@api_view(['GET'])
def get_single_user(request, username):
    """
    Function view for getting a single user with the specified UserID = id
    """
    queryset = User.objects.get(Username=username)
    serializer = UserSerializer
    permissions = None
    context = {'fields_to_drop': []}
    payload = serializer(queryset, context=context)
    return Response(payload.data)


@api_view(['POST'])
def user_update(request, username):
    user = User.objects.get(Username=username)
    contact = Contact.objects.get(ContactID=user.ContactID.ContactID)
    data = json.loads(request.body.decode('utf-8'))
    for (key, value) in data.items():
        setattr(user, key, value)
        setattr(contact, key, value)
    user.save()
    contact.save()
    return HttpResponse('')



@api_view(['GET'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def create_api_token(request):
    user = request.user
    APIToken.objects.filter(user=user).delete()
    api_token = APIToken.objects.create(user=user)
    return Response({'auth_token': api_token.key}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def set_ahj_maintainer(request):
    """
    View to assign a user as a data maintainer of an AHJ
    Expects a Username and a the primary key of an AHJ (AHJPK)
    """
    username = request.data.get('Username', None)
    if username is None:
        return Response('Missing username', status=status.HTTP_400_BAD_REQUEST)
    ahjpk = request.data.get('AHJPK', None)
    if ahjpk is None:
        return Response('Missing AHJPK', status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(Username=username)
    ahj = AHJ.objects.get(AHJPK=ahjpk)
    maintainer_record = AHJUserMaintains.objects.filter(AHJPK=ahj).filter(UserID=user)
    if maintainer_record.exists():
        maintainer_record.update(MaintainerStatus=True)
    else:
        AHJUserMaintains.objects.create(UserID=user, AHJPK=ahj, MaintainerStatus=True)
    return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


@api_view(['POST'])
def remove_ahj_maintainer(request):
    """
    View to revoke a user as a data maintainer of an AHJ
    Expects a user's webpage token and a the primary key of an AHJ (AHJPK)
    """
    username = request.data.get('Username', None)
    if username is None:
        return Response('Missing username', status=status.HTTP_400_BAD_REQUEST)
    ahjpk = request.data.get('AHJPK', None)
    if ahjpk is None:
        return Response('Missing AHJPK', status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(Username=username)
    ahj = AHJ.objects.get(AHJPK=ahjpk)
    AHJUserMaintains.objects.filter(AHJPK=ahj).filter(UserID=user).update(MaintainerStatus=False)
    return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
