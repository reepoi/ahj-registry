from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .authentication import WebpageTokenAuth
from .models import User, Comment, Edit, SubscribedChannels
from .serializers import SubscribedChannelsSerializer
from .utils import UserSerializer, CommentSerializer, EditSerializer

import datetime


@api_view(['GET'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def form_validator(request):
    """
    API call to validate the form information when a new user signs up
    """
    Username = request.GET.get('Username', None)
    Email = request.GET.get('Email', None)
    usernameExists = User.objects.filter(Username=Username).exists()
    emailExists = User.objects.filter(Email=Email).exists()
    return Response({"UsernameExists": usernameExists, "EmailExists": emailExists}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def user_comments(request):
    """
    Endpoint to get all the comments made by a specific user.
    """
    UserID = request.query_params.get('UserID', None)
    comments = Comment.objects.filter(UserID=int(UserID))
    return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def comment_submit(request):
    """
    Endpoint to submit a new user comment.
    """
    comment_text = request.data.get('CommentText', None)
    if comment_text is None:
        return Response('Missing comment text', status=status.HTTP_400_BAD_REQUEST)
    AHJPK = request.data.get('AHJPK', None)
    ReplyingTo = request.data.get('ReplyingTo', None)
    comment = Comment.objects.create(UserID=User.objects.get(Email=request.user),
                                     AHJPK=AHJPK,
                                     CommentText=comment_text, ReplyingTo=ReplyingTo)
    # send the serialized comment back to the front-end
    return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def user_edits(request):
    """
    Endpoint to get all edits made by the user with `UserID`.
    """
    UserID = request.query_params.get('UserID', None)
    edits = Edit.objects.filter(ChangedBy=UserID)
    return Response(EditSerializer(edits, many=True).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def create_chat_room(request):
    """
    Endpoint to create a new message channel
    """
    participants = request.data.get("Messagees", [])
    user = request.data.get("Messager", None)
    # create a new subscribed channel for the creating user (owner of the channel)
    channel = SubscribedChannels.objects.create(UserID=User.objects.get(Username=user),
                                                LastReadToken=str(int(datetime.datetime.now().timestamp()) * 10**7))
    # create a new subscribed channel for each of the participants
    for u in participants:
        SubscribedChannels.objects.create(UserID=User.objects.get(Username=u),
                                          ChannelID=channel.ChannelID,
                                          LastReadToken=str(int(datetime.datetime.now().timestamp()) * 10**7))
    return Response(SubscribedChannelsSerializer(
        SubscribedChannels.objects.get(ChannelID=channel.ChannelID,
                                       UserID=User.objects.get(Username=user))).data)


@api_view(['POST'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def reset_last_read(request):
    """
    Endpoint to reset the token that is marked as "last read" for the user.
    """
    obj = SubscribedChannels.objects.get(UserID=request.user,
                                         ChannelID=request.data.get('ChannelID', None))
    obj.LastReadToken = request.data.get('Token', None)
    obj.save()
    return Response(status=status.HTTP_200_OK)
