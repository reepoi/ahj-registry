from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .authentication import WebpageTokenAuth
from .models import User, Comment, Edit
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
