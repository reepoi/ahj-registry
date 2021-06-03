import django.contrib.admin
from django import forms
from django.contrib.admin.widgets import ManyToManyRawIdWidget
from django.forms.utils import ErrorList
from django.urls import reverse

from ..models import AHJ, User, AHJUserMaintains


class AHJOfficialRawIdWidget(ManyToManyRawIdWidget):
    """
    Widget made to work alongside JavaScript in its template
    to manage the many-to-many relationship between Users and AHJs.
    """
    template_name = 'admin/is_ahj_official_raw_id_field.html'

    def get_context(self, name, value, attrs):
        """
        Generate a context for the template with information to add
        Django's related lookup search, and to help the JavaScript
        create a dynamic list of AHJs the User is related to.
        """
        context = super().get_context(name, value, attrs)
        rel_to = self.rel.model
        if rel_to in django.contrib.admin.site._registry:
            context['related_url'] = reverse(
                viewname=f'admin:{rel_to._meta.app_label}_{rel_to._meta.model_name.lower()}_changelist',
                current_app=django.contrib.admin.site.name,
            ) + f'?_to_field={rel_to._meta.pk.name}'
            # The related object is registered with the same AdminSite
            context['widget']['attrs']['class'] = 'vManyToManyRawIdAdminField'
            # Template for creating links to the AHJs the User is related to for the JavaScript to fill in.
            context['base_change_url'] = reverse(f'admin:{rel_to._meta.app_label}_{rel_to._meta.model_name.lower()}_change', args=(0,))
            context['base_change_url'] = context['base_change_url'].replace('0', '%(pk)s')
            # Label the AHJ objects
            context['object_label'] = rel_to.__name__
        return context


class UserResetPasswordForm(forms.Form):
    password = forms.CharField(max_length=100)


class UserDeleteToggleAPITokenForm(forms.Form):
    toggle = forms.ChoiceField(choices=[('DoNothing', 'Do Nothing'),
                                        ('On', 'On'),
                                        ('Off', 'Off')], initial='Do Nothing',
                               label='Toggle Token')
    delete_token = forms.BooleanField(initial=False)


class UserChangeForm(forms.ModelForm):
    """
    Django User model admin change form with the 'IsAHJOfficialOf' field added.
    """
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, instance=None, use_required_attribute=None,
                 renderer=None):
        """
        Overridden to populate the 'IsAHJOfficialOf' field values.
        """
        super().__init__(data, files, auto_id, prefix,
                         initial, error_class, label_suffix,
                         empty_permitted, instance, use_required_attribute,
                         renderer)
        if instance is not None:
            self.fields['IsAHJOfficialOf'].initial = AHJUserMaintains.objects.filter(UserID=instance).values_list('AHJPK', flat=True)

    def save(self, commit=True):
        """
        Overridden to have the changes made to the 'IsAHJOfficialOf' field.
        """
        instance = super().save(commit)
        if 'IsAHJOfficialOf' in self.changed_data:
            # The AHJs entered into the field.
            form_ahjs = self.cleaned_data['IsAHJOfficialOf']
            # The AHJPK of the AHJs the User is related to.
            current_ahjpks = AHJUserMaintains.objects.filter(UserID=instance).values_list('AHJPK', flat=True)
            # Create relations for the newly added AHJs.
            ahjs_to_save = [ahj for ahj in form_ahjs if ahj.AHJPK not in current_ahjpks]
            AHJUserMaintains.objects.bulk_create([
                AHJUserMaintains(UserID=instance, AHJPK=ahj, MaintainerStatus=True) for ahj in ahjs_to_save
            ])
            # Delete relations of the removed AHJs.
            ahjs_to_delete = AHJUserMaintains.objects.filter(UserID=instance).exclude(AHJPK__in=form_ahjs)
            ahjs_to_delete.delete()
        return instance

    IsAHJOfficialOf = forms.ModelMultipleChoiceField(queryset=AHJ.objects.all(),
                                                     required=False,
                                                     label='Is AHJ Official Of',
                                                     widget=AHJOfficialRawIdWidget(rel=AHJ.objects,
                                                                                   admin_site=django.contrib.admin.site))

    class Meta:
        model = User
        fields = '__all__'
