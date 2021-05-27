from django import forms


class UserResetPasswordForm(forms.Form):
    password = forms.CharField(max_length=100)
