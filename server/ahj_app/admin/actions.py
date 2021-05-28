from django.core.checks import messages
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .form import UserResetPasswordForm, UserDeleteToggleAPITokenForm
from ..models import User, APIToken
from ..usf import dict_filter_keys_start_with


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
        user_id = request.POST['_selected_action']
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
    """
    Admin action for the User model. The admin can select one or
    more users and generate an API token for them. If selected users
    already have an API token, a new API will not be generated for them.
    """
    if 'apply' in request.POST:
        """
        The form has been filled out and submitted.
        """
        for user_id in request.POST.getlist('_selected_action'):
            """
            Create an API token for each user without one.
            """
            user = User.objects.get(UserID=user_id)
            APIToken.objects.create(user=user)
        self.message_user(request, 'Success', level=messages.INFO)
        return HttpResponseRedirect(request.get_full_path())
    users_with_tokens = queryset.exclude(api_token=None).order_by('Email')
    users_without_tokens = queryset.filter(api_token=None).order_by('Email')
    return render(request, 'admin/user_generate_api_token.html', context={
        'request': request,
        'users_without_tokens': users_without_tokens,
        'users_with_tokens': users_with_tokens
    })


user_generate_api_token.short_description = 'Generate API token'


def user_delete_toggle_api_token(self, request, queryset):
    """
    Admin action for the User model. The admin can select one or
    more users and delete or toggle on/off each user's API token.
     If selected users do not have an API token, there will be no
     options displayed for them.
    """
    if 'apply' in request.POST:
        """
        The form has been filled out and submitted.
        """
        print(request.POST)
        user_to_form_pairs = [pair.split('.') for pair in request.POST.getlist('user_to_form')]
        for user_id, form_prefix in user_to_form_pairs:
            user = User.objects.get(UserID=user_id)
            form_data = dict_filter_keys_start_with(form_prefix, request.POST)
            toggle_api_token = form_data.get('toggle', '')
            delete_api_token = form_data.get('delete_token', '')
            if toggle_api_token == 'On':
                user.api_token.is_active = True
                user.api_token.save()
            elif toggle_api_token == 'Off':
                user.api_token.is_active = False
                user.api_token.save()
            if delete_api_token == 'on':
                user.api_token.delete()
        self.message_user(request, 'Success', level=messages.INFO)
        return HttpResponseRedirect(request.get_full_path())
    users_with_tokens = queryset.exclude(api_token=None).order_by('Email')
    users_without_tokens = queryset.filter(api_token=None).order_by('Email')
    formset = formset_factory(UserDeleteToggleAPITokenForm, extra=queryset.count())()
    return render(request, 'admin/user_delete_toggle_api_token.html', context={
        'request': request,
        'users_without_tokens': users_without_tokens,
        'formtuples': zip(users_with_tokens, formset),
        'users_with_tokens': users_with_tokens
    })


user_delete_toggle_api_token.short_description = 'Delete/Toggle API Token'
