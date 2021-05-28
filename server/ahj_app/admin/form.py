from django import forms


class UserResetPasswordForm(forms.Form):
    password = forms.CharField(max_length=100)


class UserDeleteToggleAPITokenForm(forms.Form):
    toggle = forms.ChoiceField(choices=[('DoNothing', 'Do Nothing'),
                                        ('On', 'On'),
                                        ('Off', 'Off')], initial='Do Nothing',
                               label='Toggle Token')
    delete_token = forms.BooleanField(initial=False)
