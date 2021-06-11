import datetime

from django.core.checks import messages
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .form import UserResetPasswordForm, UserDeleteToggleAPITokenForm
from ..models import User, APIToken, Edit
from ..usf import dict_filter_keys_start_with


def reset_password(user, raw_password):
    """
    Sets and saves a user's password.
    """
    user.set_password(raw_password)
    user.save()


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
        reset_password(user, password)
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


def partition_by_field(queryset, field, value):
    """
    Returns two querysets from the queryset:
     - queryset of rows whose field value matches the value
     - queryset of rows whose field value does not match the value
    """
    with_field_value = queryset.filter(**{field: value})
    without_field_value = queryset.exclude(**{field: value})
    return with_field_value, without_field_value


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
    users_without_tokens, users_with_tokens = partition_by_field(queryset, 'api_token', None)
    users_with_tokens = users_with_tokens.order_by('Email')
    users_without_tokens = users_without_tokens.order_by('Email')
    return render(request, 'admin/user_generate_api_token.html', context={
        'request': request,
        'users_without_tokens': users_without_tokens,
        'user_token_tuples': zip(users_with_tokens, users_with_tokens.values_list('api_token', flat=True))
    })


user_generate_api_token.short_description = 'Generate API token'


def delete_toggle_api_token(user, toggle=None, delete=False):
    """
    Modifies a user's API token by either deleting it or toggling it on/off.
    """
    if not hasattr(user, 'api_token'):
        return
    if delete:
        user.api_token.delete()
        return
    if toggle is not None:
        user.api_token.is_active = toggle
        user.api_token.save()


def set_toggle(form_value):
    """
    Used with an HTML dropdown input with values:
    'On', 'Off','DoNothing'
    """
    if form_value == 'On':
        return True
    elif form_value == 'Off':
        return False
    else:
        return None


def set_delete(form_value):
    """
    Return True if form_value is 'on'.
    Used with an HTML checkbox input.
    """
    if form_value == 'on':
        return True
    return False


def process_delete_toggle_api_token_data(post_data):
    """
    This expects the post_data to contain an array called 'user_to_form'.
    Each item in this array is of the form:
     - '<UserID>.<form_prefix>' (i.e. '1.form-0')
    Each form then may add two form data key-value pairs:
     - '<form_prefix>-toggle': '<On,Off,DoNothing>' (i.e. 'form-0-toggle': 'On')
     - '<form_prefix>-delete_token': 'on' (i.e. 'form-0-delete_token': 'on')
    """
    user_to_form_pairs = [pair.split('.') for pair in post_data.getlist('user_to_form')]
    user_form_data = []
    for user_id, form_prefix in user_to_form_pairs:
        user = User.objects.get(UserID=user_id)
        form_data = dict_filter_keys_start_with(form_prefix, post_data)
        toggle_api_token = form_data.get('toggle', '')
        delete_api_token = form_data.get('delete_token', '')
        user_form_data.append({'user': user,
                               'toggle': set_toggle(toggle_api_token),
                               'delete': set_delete(delete_api_token)})
    return user_form_data


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
        action_data = process_delete_toggle_api_token_data(request.POST)
        for item in action_data:
            delete_toggle_api_token(user=item['user'], toggle=item['toggle'], delete=item['delete'])
        self.message_user(request, 'Success', level=messages.INFO)
        return HttpResponseRedirect(request.get_full_path())
    users_without_tokens, users_with_tokens = partition_by_field(queryset, 'api_token', None)
    users_with_tokens = users_with_tokens.order_by('Email')
    users_without_tokens = users_without_tokens.order_by('Email')
    formset = formset_factory(UserDeleteToggleAPITokenForm, extra=queryset.count())()
    return render(request, 'admin/user_delete_toggle_api_token.html', context={
        'request': request,
        'users_without_tokens': users_without_tokens,
        'users_and_forms': zip(users_with_tokens, formset),
        'users_with_tokens': users_with_tokens
    })


user_delete_toggle_api_token.short_description = 'Delete/Toggle API Token'


def process_approve_edits_data(post_data):
    """
    This expects the post_data to contain an array called 'edit_to_form'.
    Each item in this array is of the form:
     - '<EditID>.<form_prefix>' (i.e. '1.form-0')
    Each form then may add two form data key-value pairs:
     - '<form_prefix>-date_effective': '<date>' (i.e. 'form-0-date_effective': '06-04-2021')
    """
    edit_to_form_pairs = [pair.split('.') for pair in post_data.getlist('edit_to_form')]
    edit_form_data = []
    for edit_id, form_prefix in edit_to_form_pairs:
        edit = Edit.objects.get(EditID=edit_id)
        form_data = dict_filter_keys_start_with(form_prefix, post_data)
        date_effective = datetime.datetime.strptime(form_data.get('date_effective', ''), '%Y-%m-%d').date()
        edit_form_data.append({'edit': edit,
                               'date_effective': date_effective,
                               'apply_now': date_effective == datetime.date.today()})
    return edit_form_data


def edit_approve_edits(self, request, queryset):
    if 'apply' in request.POST:
        pass
    pass
