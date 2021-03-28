from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import User, Comment, Edit
from .utils import filter_users, UserSerializer, CommentSerializer, EditSerializer


@api_view(['GET'])
def get_leaderboard_users(request):
    users = filter_users(request)
    serializer = UserSerializer
    payload = serializer(users, many=True)
    return Response(payload.data)


@api_view(['GET'])
def form_validator(request):
    Username = request.GET.get('Username', None)
    Email = request.GET.get('Email', None)
    usernameExists = User.objects.filter(Username=Username).exists()
    emailExists = User.objects.filter(Email=Email).exists()
    return Response({"Username": usernameExists, "Email": emailExists})


@api_view(['GET'])
def user_comments(request):
    UserID = request.query_params.get('UserID', None)
    comments = Comment.objects.filter(UserID=int(UserID))
    return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)


@api_view(['POST'])
def comment_submit(request):
    # TODO: set UserID of comment to request.user
    comment_text = request.data.get('CommentText', None)
    if comment_text is None:
        return Response('Missing comment text', status=status.HTTP_400_BAD_REQUEST)
    AHJPK = request.data.get('AHJPK', None)
    ReplyingTo = request.data.get('ReplyingTo', None)
    comment = Comment.objects.create(UserID=User.objects.get(Email=request.user),
                                     AHJPK=AHJPK,
                                     CommentText=comment_text, ReplyingTo=ReplyingTo)
    return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_edits(request):
    UserID = request.query_params.get('UserID', None)
    edits = Edit.objects.filter(ChangedBy=UserID)
    return Response(EditSerializer(edits, many=True).data, status=status.HTTP_200_OK)
