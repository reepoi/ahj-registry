from collections import OrderedDict
from typing import Dict

from djoser.compat import get_user_email, get_user_email_field_name
from django.conf import settings
from django.db import connection
from rest_framework import serializers
from rest_framework_gis import serializers as geo_serializers
from djoser.serializers import UserCreateSerializer
from .models import *


class PolygonSerializer(geo_serializers.GeoFeatureModelSerializer):
    AHJID = serializers.SerializerMethodField()

    class Meta:
        model = Polygon
        geo_field = 'Polygon'
        id_field = False
        fields = ['AHJID', 'LandArea', 'GEOID', 'InternalPLatitude', 'InternalPLongitude']

    def get_AHJID(self, instance):
        return self.context.get('AHJID', '')

class OrangeButtonSerializer(serializers.Field):
    def get_attribute(self, instance):
        attribute = super().get_attribute(instance)
        if attribute is None:
            return {'Value': None}
        else:
            return attribute

    def to_representation(self, value):
        if type(value) is dict and 'Value' in value and value['Value'] is None:
            return value
        ob_obj = {}
        ob_obj['Value'] = value
        return ob_obj

class EnumModelSerializer(serializers.Serializer):
    Value = serializers.CharField()

    def get_attribute(self, instance):
        attribute = super().get_attribute(instance)
        if attribute is None:
            return {'Value': ''}
        else:
            return attribute

    def to_representation(self, value):
        if type(value) is dict and 'Value' in value and value['Value'] == '':
            return value
        return super().to_representation(value)


class FeeStructureSerializer(serializers.Serializer):
    FeeStructurePK = OrangeButtonSerializer()
    FeeStructureID = OrangeButtonSerializer()
    FeeStructureName = OrangeButtonSerializer()
    FeeStructureType = EnumModelSerializer()
    Description = OrangeButtonSerializer()
    FeeStructureStatus = OrangeButtonSerializer()

    def to_representation(self, feestructure):
        if self.context.get('is_public_view', False):
            for field in FeeStructure.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(feestructure)

class LocationSerializer(serializers.Serializer):
    LocationID = OrangeButtonSerializer()
    Altitude = OrangeButtonSerializer()
    Elevation = OrangeButtonSerializer()
    Latitude = OrangeButtonSerializer()
    Longitude = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    LocationDeterminationMethod = EnumModelSerializer()
    LocationType = EnumModelSerializer()

    def to_representation(self, location):
        if self.context.get('is_public_view', False):
            for field in Location.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(location)

class AddressSerializer(serializers.Serializer):
    AddressID = OrangeButtonSerializer()
    AddrLine1 = OrangeButtonSerializer()
    AddrLine2 = OrangeButtonSerializer()
    AddrLine3 = OrangeButtonSerializer()
    City = OrangeButtonSerializer()
    Country = OrangeButtonSerializer()
    County = OrangeButtonSerializer()
    StateProvince = OrangeButtonSerializer()
    ZipPostalCode = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    AddressType = EnumModelSerializer()
    Location = LocationSerializer(source='LocationID')

    def to_representation(self, address):
        if self.context.get('is_public_view', False):
            for field in Address.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(address)

class ContactSerializer(serializers.Serializer):
    ContactID = OrangeButtonSerializer()
    FirstName = OrangeButtonSerializer()
    MiddleName = OrangeButtonSerializer()
    LastName = OrangeButtonSerializer()
    HomePhone = OrangeButtonSerializer()
    MobilePhone = OrangeButtonSerializer()
    WorkPhone = OrangeButtonSerializer()
    ContactType = EnumModelSerializer()
    ContactTimezone = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    Email = OrangeButtonSerializer()
    Title = OrangeButtonSerializer()
    URL = OrangeButtonSerializer()
    PreferredContactMethod = EnumModelSerializer()
    Address = AddressSerializer(source='AddressID')

    def to_representation(self, contact):
        if self.context.get('is_public_view', False):
            for field in Contact.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(contact)

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class UserSerializer(serializers.Serializer):
    UserID = serializers.IntegerField(read_only=True)
    ContactID = ContactSerializer()
    Username = serializers.CharField()
    Email = serializers.CharField()
    PersonalBio = serializers.CharField()
    CompanyAffiliation = serializers.CharField()
    Photo = serializers.CharField()
    AcceptedEdits = serializers.IntegerField()
    SubmittedEdits = serializers.IntegerField()
    CommunityScore = serializers.IntegerField()
    SignUpDate = serializers.DateField()
    MaintainedAHJs = serializers.ListField(source='get_maintained_ahjs')
    APIToken = serializers.CharField(source='get_API_token')

class UserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('UserID', 'ContactID', 'Username', 'password', 'Email', 'is_staff', 'is_active', 'SignUpDate', 'PersonalBio', 'URL', 'CompanyAffiliation', 'Photo', 'CommunityScore', 'SecurityLevel')

class CommentSerializer(serializers.Serializer):
    CommentID = OrangeButtonSerializer()
    User = UserSerializer(source='UserID')
    CommentText = OrangeButtonSerializer()
    Date = OrangeButtonSerializer()
    Replies = RecursiveField(source='get_replies', many=True)

class DocumentSubmissionMethodUseSerializer(serializers.Serializer):
    UseID = serializers.IntegerField()
    Value = serializers.CharField(source='get_value')

    def to_representation(self, dsmu):
        if self.context.get('is_public_view', False):
            for field in AHJDocumentSubmissionMethodUse.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(dsmu)

class PermitIssueMethodUseSerializer(serializers.Serializer):
    UseID = serializers.IntegerField()
    Value = serializers.CharField(source='get_value')

    def to_representation(self, pimu):
        if self.context.get('is_public_view', False):
            for field in AHJPermitIssueMethodUse.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(pimu)

class AHJInspectionSerializer(serializers.Serializer):
    InspectionID = OrangeButtonSerializer()
    InspectionType = EnumModelSerializer()
    AHJInspectionName = OrangeButtonSerializer()
    AHJInspectionNotes = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    FileFolderURL = OrangeButtonSerializer()
    TechnicianRequired = OrangeButtonSerializer()
    InspectionStatus = OrangeButtonSerializer()
    Contacts = ContactSerializer(source='get_contacts', many=True)
    UnconfirmedContacts = ContactSerializer(source='get_uncon_con', many=True)

    def to_representation(self, inspection):
        if self.context.get('is_public_view', False):
            for field in AHJInspection.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(inspection)

class EngineeringReviewRequirementSerializer(serializers.Serializer):
    EngineeringReviewRequirementID = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    EngineeringReviewType = EnumModelSerializer()
    RequirementLevel = EnumModelSerializer()
    RequirementNotes = OrangeButtonSerializer()
    StampType = EnumModelSerializer()
    EngineeringReviewRequirementStatus = OrangeButtonSerializer()

    def to_representation(self, err):
        if self.context.get('is_public_view', False):
            for field in EngineeringReviewRequirement.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(err)

class AHJSerializer(serializers.Serializer):
    AHJPK = OrangeButtonSerializer()
    AHJID = OrangeButtonSerializer()
    AHJCode = OrangeButtonSerializer()
    AHJLevelCode = EnumModelSerializer()
    AHJName = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    DocumentSubmissionMethodNotes = OrangeButtonSerializer()
    PermitIssueMethodNotes = OrangeButtonSerializer()
    EstimatedTurnaroundDays = OrangeButtonSerializer()
    FileFolderURL = OrangeButtonSerializer()
    URL = OrangeButtonSerializer()
    BuildingCode = EnumModelSerializer()
    BuildingCodeNotes = OrangeButtonSerializer()
    ElectricCode = EnumModelSerializer()
    ElectricCodeNotes = OrangeButtonSerializer()
    FireCode = EnumModelSerializer()
    FireCodeNotes = OrangeButtonSerializer()
    ResidentialCode = EnumModelSerializer()
    ResidentialCodeNotes = OrangeButtonSerializer()
    WindCode = EnumModelSerializer()
    WindCodeNotes = OrangeButtonSerializer()
    Address = AddressSerializer(source='AddressID')
    Contacts = ContactSerializer(source='get_contacts', many=True)
    UnconfirmedContacts = ContactSerializer(source='get_unconfirmed', many=True)
    UnconfirmedInspections = AHJInspectionSerializer(source='get_unconfirmed_inspections', many=True)
    Polygon = serializers.SerializerMethodField()
    Comments = CommentSerializer(source='get_comments', many=True)
    AHJInspections = AHJInspectionSerializer(source='get_inspections', many=True)
    DocumentSubmissionMethods = DocumentSubmissionMethodUseSerializer(source='get_document_submission_methods', many=True)
    UnconfirmedDocumentSubmissionMethods = DocumentSubmissionMethodUseSerializer(source='get_uncon_dsm', many=True)
    PermitIssueMethods = PermitIssueMethodUseSerializer(source='get_permit_submission_methods', many=True)
    UnconfirmedPermitIssueMethods = PermitIssueMethodUseSerializer(source='get_uncon_pim', many=True)
    EngineeringReviewRequirements = EngineeringReviewRequirementSerializer(source='get_err', many=True)
    UnconfirmedEngineeringReviewRequirements = EngineeringReviewRequirementSerializer(source='get_uncon_err', many=True)
    FeeStructures = FeeStructureSerializer(source='get_fee_structures', many=True)
    UnconfirmedFeeStructures = FeeStructureSerializer(source='get_uncon_fs', many=True)

    def to_representation(self, ahj):
        if self.context.get('is_public_view', False):
            for field in AHJ.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(ahj)

    def get_Polygon(self, instance):
        if instance.PolygonID is None:
            return None
        return PolygonSerializer(instance.PolygonID, context={'AHJID': instance.AHJID}).data

class EditSerializer(serializers.Serializer):
    EditID = serializers.IntegerField(read_only=True)
    ChangedBy = UserSerializer()
    ApprovedBy = UserSerializer()
    AHJPK = serializers.IntegerField(source='AHJPK.AHJPK')
    SourceTable = serializers.CharField()
    SourceColumn = serializers.CharField()
    SourceRow = serializers.IntegerField()
    ReviewStatus = serializers.CharField()
    OldValue = serializers.CharField(read_only=True)
    NewValue = serializers.CharField()
    DateRequested = serializers.DateTimeField(read_only=True)
    DateEffective = serializers.DateTimeField(read_only=True)
    EditType = serializers.CharField()
    DataSourceComment = serializers.CharField()

    def to_representation(self, edit):
        if self.context.get('drop_users', False):
            """
            This gives the option for callers of the serializer to only serialize the username of the user.
            """
            self.fields['ChangedBy'] = serializers.CharField(source='ChangedBy.Username')
            if edit.ApprovedBy is None:
                self.fields['ApprovedBy'] = UserSerializer()
            else:
                self.fields['ApprovedBy'] = serializers.CharField(source='ApprovedBy.Username')
        return super().to_representation(edit)

    def create(self):
        return Edit(**self.validated_data)

class WebpageTokenSerializer(serializers.Serializer):
    auth_token = serializers.CharField(source='key')
    User = UserSerializer(source='get_user')


# Serializer used in Djoser's password reset endpoint. 
class UserFunctionsMixin:
    def get_user(self):
        try:
            user = User._default_manager.get(
                **{self.email_field: self.data.get(self.email_field, "")},
            )
            if user.has_usable_password():
                return user
        except User.DoesNotExist:
            pass
        if (
            settings.PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND
            or settings.USERNAME_RESET_SHOW_EMAIL_NOT_FOUND
        ):
            self.fail("email_not_found")

# Serializer used in Djoser's password reset endpoint
class SendEmailResetSerializer(serializers.Serializer, UserFunctionsMixin):
    default_error_messages = {
        "email_not_found": "User with given email does not exist."
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.email_field = get_user_email_field_name(User)
        self.fields[self.email_field] = serializers.EmailField()
