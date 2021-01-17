from rest_framework import serializers
from ahj_gis.serializers import PolygonSerializer
from rest_framework.renderers import JSONRenderer
from .models import *


class EditSerializerHelper(serializers.BaseSerializer):
    def to_representation(self, value):
        if value.__class__.__name__ == self.field_name[0:-2] and self.field_name[-2:].lower() == 'id':
            return EditSerializer(value.get_create_edit(self.parent.context['confirmed_edits_only'], self.parent.context['highest_vote_rating']), hide_ui_fields=self.parent.context['hide_ui_fields'], called_by_view=self.parent.context['called_by_view']).data
        if value.__class__.__name__ in ['DocumentSubmissionMethod', 'PermitIssueMethod']:
            field_name = value.__class__.__name__
        else:
            field_name = self.field_name
        return EditSerializer(value.get_edit(field_name, self.parent.context['confirmed_edits_only'], self.parent.context['highest_vote_rating']), hide_ui_fields=self.parent.context['hide_ui_fields'], called_by_view=self.parent.context['called_by_view']).data

    def to_internal_value(self, data):
        pass

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class UserSerializer(serializers.Serializer):
    UserID = serializers.IntegerField(source='id', required=False, read_only=True)
    Email = serializers.CharField(source='email_address')
    Password = serializers.CharField(source='password', write_only=True)
    FirstName = serializers.CharField(source='first_name')
    LastName = serializers.CharField(source='last_name')
    AHJ = serializers.UUIDField(source='AHJ__AHJID', read_only=True)

    def create(self, validated_data):
        Email = validated_data.get('email_address', '')
        Password = validated_data.get('password', '')
        FirstName = validated_data.get('first_name', '')
        LastName = validated_data.get('last_name', '')
        user = User.objects.create_user(email_address=Email, password=Password, first_name=FirstName, last_name=LastName, is_active=False)
        send_user_confirmation_email(user)
        return user

    def update(self, instance, validated_data):
        pass


class EditSerializer(serializers.Serializer):
    EditID = serializers.IntegerField(source='id', required=False, read_only=True)
    RecordID = serializers.CharField(required=False)
    RecordType = serializers.CharField(required=False)
    EditType = serializers.CharField(required=False)
    ParentID = serializers.CharField(required=False)
    ParentRecordType = serializers.CharField(required=False)
    PreviousValue = serializers.CharField(required=False, read_only=True)
    FieldName = serializers.CharField(required=False)
    Value = serializers.CharField(required=False, allow_blank=True)
    IsConfirmed = serializers.NullBooleanField(required=False, read_only=True)
    ConfirmingUserID = UserSerializer(source='get_user_confirm', required=False, read_only=True)
    ModifyingUserID = UserSerializer(source='get_user_modify', required=False, read_only=True)
    ModifiedDate = serializers.DateTimeField(required=False, read_only=True)
    VoteRating = serializers.IntegerField(required=False, read_only=True)

    def __init__(self, *args, **kwargs):
        called_by_view = kwargs.pop('called_by_view', False)
        hide_ui_fields = kwargs.pop('hide_ui_fields', True)
        super(EditSerializer, self).__init__(*args, **kwargs)
        if called_by_view is True and hide_ui_fields is True:
            excluded_field_names = ['EditID', 'RecordID', 'RecordType', 'EditType', 'ParentID', 'ParentRecordType',
                                    'PreviousValue', 'FieldName', 'IsConfirmed', 'ConfirmingUserID', 'ModifyingUserID',
                                    'ModifiedDate', 'VoteRating']
            for field in excluded_field_names:
                self.fields.pop(field)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class LocationSerializer(serializers.Serializer):
    LocationID = EditSerializerHelper(source='*', required=False)
    Altitude = EditSerializerHelper(source='*', required=False)
    Description = EditSerializerHelper(source='*', required=False)
    Elevation = EditSerializerHelper(source='*', required=False)
    Latitude = EditSerializerHelper(source='*', required=False)
    LocationDeterminationMethod = EditSerializerHelper(source='*', required=False)
    LocationType = EditSerializerHelper(source='*', required=False)
    Longitude = EditSerializerHelper(source='*', required=False)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class AddressSerializer(serializers.Serializer):
    AddressID = EditSerializerHelper(source='*', required=False)
    AddrLine1 = EditSerializerHelper(source='*', required=False)
    AddrLine2 = EditSerializerHelper(source='*', required=False)
    AddrLine3 = EditSerializerHelper(source='*', required=False)
    AddressType = EditSerializerHelper(source='*', required=False)
    City = EditSerializerHelper(source='*', required=False)
    Country = EditSerializerHelper(source='*', required=False)
    County = EditSerializerHelper(source='*', required=False)
    Description = EditSerializerHelper(source='*', required=False)
    StateProvince = EditSerializerHelper(source='*', required=False)
    ZipPostalCode = EditSerializerHelper(source='*', required=False)
    Location = LocationSerializer(source='location', many=False, required=False, allow_null=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ContactSerializer(serializers.Serializer):
    ContactID = EditSerializerHelper(source='*', required=False)
    ContactType = EditSerializerHelper(source='*', required=False)
    ContactTimezone = EditSerializerHelper(source='*', required=False)
    Description = EditSerializerHelper(source='*', required=False)
    Email = EditSerializerHelper(source='*', required=False)
    FirstName = EditSerializerHelper(source='*', required=False)
    HomePhone = EditSerializerHelper(source='*', required=False)
    LastName = EditSerializerHelper(source='*', required=False)
    MiddleName = EditSerializerHelper(source='*', required=False)
    MobilePhone = EditSerializerHelper(source='*', required=False)
    WorkPhone = EditSerializerHelper(source='*', required=False)
    Title = EditSerializerHelper(source='*', required=False)
    PreferredContactMethod = EditSerializerHelper(source='*', required=False)
    URL = EditSerializerHelper(source='*', required=False)
    Address = AddressSerializer(source='address', many=False, required=False, allow_null=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class AHJInspectionSerializer(serializers.Serializer):
    AHJInspectionName = EditSerializerHelper(source='*', required=False)
    AHJInspectionNotes = EditSerializerHelper(source='*', required=False)
    Description = EditSerializerHelper(source='*', required=False)
    FileFolderURL = EditSerializerHelper(source='*', required=False)
    InspectionType = EditSerializerHelper(source='*', required=False)
    TechnicianRequired = EditSerializerHelper(source='*', required=False)
    Contacts = ContactSerializer(source='contact_set', many=True, required=False)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class EngineeringReviewRequirementSerializer(serializers.Serializer):
    RequirementLevel = EditSerializerHelper(source='*', required=False)
    RequirementNotes = EditSerializerHelper(source='*', required=False)
    StampType = EditSerializerHelper(source='*', required=False)
    Description = EditSerializerHelper(source='*', required=False)
    EngineeringReviewType = EditSerializerHelper(source='*', required=False)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class FeeStructureSerializer(serializers.Serializer):
    Description = EditSerializerHelper(source='*', required=False)
    FeeStructureID = EditSerializerHelper(source='*', required=False)
    FeeStructureName = EditSerializerHelper(source='*', required=False)
    FeeStructureType = EditSerializerHelper(source='*', required=False)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class AHJSerializer(serializers.Serializer):
    AHJID = EditSerializerHelper(source='*', required=False)
    AHJCode = EditSerializerHelper(source='*', required=False)
    AHJName = EditSerializerHelper(source='*', required=False)
    AHJLevelCode = EditSerializerHelper(source='*', required=False)
    BuildingCode = EditSerializerHelper(source='*', required=False)
    BuildingCodeNotes = EditSerializerHelper(source='*', required=False)
    DataSourceComments = EditSerializerHelper(source='*', required=False)
    Description = EditSerializerHelper(source='*', required=False)
    DocumentSubmissionMethods = EditSerializerHelper(source='documentsubmissionmethod_set', many=True, required=False)
    DocumentSubmissionMethodNotes = EditSerializerHelper(source='*', required=False)
    ElectricCode = EditSerializerHelper(source='*', required=False)
    ElectricCodeNotes = EditSerializerHelper(source='*', required=False)
    EstimatedTurnaroundDays = EditSerializerHelper(source='*', required=False)
    FileFolderURL = EditSerializerHelper(source='*', required=False)
    FireCode = EditSerializerHelper(source='*', required=False)
    FireCodeNotes = EditSerializerHelper(source='*', required=False)
    PermitIssueMethods = EditSerializerHelper(source='permitissuemethod_set', many=True, required=False)
    PermitIssueMethodNotes = EditSerializerHelper(source='*', required=False)
    ResidentialCode = EditSerializerHelper(source='*', required=False)
    ResidentialCodeNotes = EditSerializerHelper(source='*', required=False)
    URL = EditSerializerHelper(source='*', required=False)
    WindCode = EditSerializerHelper(source='*', required=False)
    WindCodeNotes = EditSerializerHelper(source='*', required=False)
    Address = AddressSerializer(source='address', many=False, required=False, allow_null=True)
    AHJInspections = AHJInspectionSerializer(source='ahjinspection_set', many=True, required=False)
    Contacts = ContactSerializer(source='contact_set', many=True, required=False)
    EngineeringReviewRequirements = EngineeringReviewRequirementSerializer(source='engineeringreviewrequirement_set', many=True, required=False)
    FeeStructures = FeeStructureSerializer(source='feestructure_set', many=True, required=False)
    mpoly = PolygonSerializer()

    def __init__(self, *args, **kwargs):
        hide_ui_fields = kwargs['context'].get('hide_ui_fields', True)
        super(AHJSerializer, self).__init__(*args, **kwargs)

        if hide_ui_fields is True:
            excluded_field_names = ['mpoly']
            for field in excluded_field_names:
                self.fields.pop(field)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class LocationHistorySerializer(serializers.ModelSerializer):
    history_user = UserSerializer(many=False)

    class Meta:
        model = Location.history.model
        fields = '__all__'


class AddressHistorySerializer(serializers.ModelSerializer):
    history_user = UserSerializer(many=False)

    class Meta:
        model = Address.history.model
        fields = '__all__'


class ContactHistorySerializer(serializers.ModelSerializer):
    history_user = UserSerializer(many=False)

    class Meta:
        model = Contact.history.model
        fields = '__all__'


class EngineeringReviewRequirementHistorySerializer(serializers.ModelSerializer):
    history_user = UserSerializer(many=False)

    class Meta:
        model = EngineeringReviewRequirement.history.model
        fields = '__all__'


class AHJHistorySerializer(serializers.ModelSerializer):
    history_user = UserSerializer(many=False)

    class Meta:
        model = AHJ.history.model
        fields = '__all__'
