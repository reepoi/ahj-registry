from django.core.checks import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .form import UserResetPasswordForm
from ..models import User, APIToken


def user_reset_password(self, request, queryset):
    """
    Admin action for the User model. The admin can set a new password
    for one user. The new password is hashed, and then saved.
    """
    if 'apply' in request.POST:
        """
        The form has been filled out and submitted.
        """
        password = request.POST['password']
        user_id = request.POST['_selected_action'][0]
        user = User.objects.get(UserID=user_id)
        user.set_password(password)
        user.save()
        self.message_user(request, 'Success', level=messages.INFO)
        return HttpResponseRedirect(request.get_full_path())
    if queryset.count() > 1:
        """
        Only support setting the password for one user at a time.
        """
        self.message_user(request, 'Please select one user when running this action.', level=messages.ERROR)
        return HttpResponseRedirect(request.get_full_path())
    form = UserResetPasswordForm()
    return render(request, 'admin/user_reset_password.html', context={
        'request': request,
        'user': queryset.first(),
        'form': form
    })


user_reset_password.short_description = 'Reset password'


def user_generate_api_token(self, request, queryset):
    if 'apply' in request.POST:
        """
        The form has been filled out and submitted.
        """
        for user_id in request.POST['_selected_action']:
            """
            Create an API token for each user without one.
            """
            user = User.objects.get(UserID=user_id)
            APIToken.objects.create(user=user)
        self.message_user(request, 'Success', level=messages.INFO)
        return HttpResponseRedirect(request.get_full_path())
    users_with_tokens = queryset.exclude(api_token=None)
    users_without_tokens = queryset.filter(api_token=None)
    return render(request, 'admin/user_generate_api_token.html', context={
        'request': request,
        'users_without_tokens': users_without_tokens,
        'users_with_tokens': users_with_tokens
    })


user_generate_api_token.short_description = 'Generate API token'
