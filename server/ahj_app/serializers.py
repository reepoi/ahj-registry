import datetime
from collections import OrderedDict
from typing import Tuple, Dict, Any, Optional

from django.apps import apps
from django.db import connection
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework_gis import serializers as geo_serializers
from djoser.serializers import UserCreateSerializer#, UserSerializer
from .models import *


class FindPolygonAHJID(serializers.UUIDField):
    def to_representation(self, value: Polygon) -> Optional[str]:
        # Some polygons have multiple AHJ paired with them
        # This is because there are duplicate AHJ (data issue)
        ahj = AHJ.objects.filter(PolygonID=value).first()
        if ahj is None:
            return None
        else:
            return ahj.AHJID


class PolygonSerializer(geo_serializers.GeoFeatureModelSerializer):
    AHJID = FindPolygonAHJID(source='*')

    class Meta:
        model = Polygon
        geo_field = 'Polygon'
        id_field = False
        fields = ['AHJID', 'LandArea', 'GEOID', 'InternalPLatitude', 'InternalPLongitude']


class OrangeButtonSerializer(serializers.Field):
    def to_representation(self, value: str) -> Dict[str, str]:
        ob_obj = {}
        if value is None:
            value = ''
        ob_obj['Value'] = value
        # if self.field_name == 'PermitIssueMethodNotes':
            # print('Value: ', value)
        return ob_obj

class ContactSerializer(serializers.ModelSerializer):
    ContactID = serializers.IntegerField(read_only=True)
    FirstName = serializers.CharField()
    LastName = serializers.CharField()
    MobilePhone = serializers.CharField()
    URL = serializers.CharField()
    PreferredContactMethod =  serializers.CharField()

    class Meta:
        model = Contact
        fields = ['ContactID', 'FirstName', 'LastName', 'MobilePhone', 'URL', 'PreferredContactMethod']

class FeeStructureSerializer(serializers.Serializer):
    FeeStructurePK = OrangeButtonSerializer()
    FeeStructureID = OrangeButtonSerializer()
    FeeStructureName = OrangeButtonSerializer()
    FeeStructureType = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    FeeStructureStatus = OrangeButtonSerializer()

    class Meta:
        model = FeeStructure
        fields = ['FeeStructurePK',
                  'AHJPK',
                  'FeeStructureID',
                  'FeeStructureName',
                  'FeeStructureType',
                  'Description',
                  'FeeStructureStatus']


class LocationSerializer(serializers.Serializer):
    LocationID = OrangeButtonSerializer()
    Altitude = OrangeButtonSerializer()
    Elevation = OrangeButtonSerializer()
    Latitude = OrangeButtonSerializer()
    Longitude = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    LocationDeterminationMethod = OrangeButtonSerializer()
    LocationType = OrangeButtonSerializer()


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
    AddressType = OrangeButtonSerializer()
    Location = LocationSerializer(source='LocationID')


class ContactSerializer(serializers.Serializer):
    ContactID = OrangeButtonSerializer()
    FirstName = OrangeButtonSerializer()
    MiddleName = OrangeButtonSerializer()
    LastName = OrangeButtonSerializer()
    HomePhone = OrangeButtonSerializer()
    MobilePhone = OrangeButtonSerializer()
    WorkPhone = OrangeButtonSerializer()
    ContactType = OrangeButtonSerializer()
    ContactTimezone = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    Email = OrangeButtonSerializer()
    Title = OrangeButtonSerializer()
    URL = OrangeButtonSerializer()
    PreferredContactMethod = OrangeButtonSerializer()
    Address = AddressSerializer(source='AddressID')


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
    IsPeerReviewer = serializers.IntegerField()
    NumReviewsDone = serializers.IntegerField()
    AcceptedEdits = serializers.IntegerField()
    SubmittedEdits = serializers.IntegerField()
    CommunityScore = serializers.IntegerField()
    SignUpDate = serializers.DateField()
    MaintainedAHJs = serializers.ListField(source='get_maintained_ahjs')

class UserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('UserID', 'ContactID', 'Username', 'password', 'Email', 'is_staff', 'is_active', 'SignUpDate', 'PersonalBio', 'URL', 'CompanyAffiliation', 'Photo', 'IsPeerReviewer', 'NumReviewsDone', 'CommunityScore', 'SecurityLevel')


class CommentSerializer(serializers.Serializer):
    CommentID = OrangeButtonSerializer()
    User = UserSerializer(source='UserID')
    CommentText = OrangeButtonSerializer()
    Date = OrangeButtonSerializer()
    Replies = RecursiveField(source='get_replies',many=True)

class DocumentSubmissionMethodUseSerializer(serializers.Serializer):
    UseID = serializers.IntegerField()
    Value = serializers.CharField(source='get_value')


class PermitIssueMethodUseSerializer(serializers.Serializer):
    UseID = serializers.IntegerField()
    Value = serializers.CharField(source='get_value')

class EngineeringReviewRequirementSerializer(serializers.Serializer):
    EngineeringReviewRequirementID = OrangeButtonSerializer()
    EngineeringReviewRequirementID = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    EngineeringReviewType = OrangeButtonSerializer()
    RequirementLevel = OrangeButtonSerializer()
    RequirementNotes = OrangeButtonSerializer()
    StampType = OrangeButtonSerializer()


class AHJInspectionSerializer(serializers.Serializer):
    InspectionID = OrangeButtonSerializer()
    InspectionType = OrangeButtonSerializer()
    AHJInspectionName = OrangeButtonSerializer()
    AHJInspectionNotes = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    FileFolderURL = OrangeButtonSerializer()
    TechnicianRequired = OrangeButtonSerializer()
    InspectionStatus = OrangeButtonSerializer()
    Contacts = ContactSerializer(source='get_contacts',many=True)
    UnconfirmedContacts = ContactSerializer(source='get_uncon_con',many=True)

    class Meta:
        model = AHJInspection
        fields = ['InspectionID',
                  'AHJPK',
                  'InspectionType',
                  'AHJInspectionName',
                  'AHJInspectionNotes',
                  'Description',
                  'FileFolderUrl',
                  'TechnicianRequired',
                  'InspectionStatus',
                  'Contacts']

class EngineeringReviewRequirementSerializer(serializers.Serializer):
    EngineeringReviewRequirementID = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    EngineeringReviewType = OrangeButtonSerializer()
    RequirementLevel = OrangeButtonSerializer()
    RequirementNotes = OrangeButtonSerializer()
    StampType = OrangeButtonSerializer()
    EngineeringReviewRequirementStatus = OrangeButtonSerializer()

class AHJSerializer(serializers.Serializer):
    AHJPK = OrangeButtonSerializer()
    AHJID = OrangeButtonSerializer()
    AHJCode = OrangeButtonSerializer()
    AHJLevelCode = OrangeButtonSerializer()
    AHJName = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    DocumentSubmissionMethodNotes = OrangeButtonSerializer()
    PermitIssueMethodNotes = OrangeButtonSerializer()
    EstimatedTurnaroundDays = OrangeButtonSerializer()
    FileFolderURL = OrangeButtonSerializer()
    URL = OrangeButtonSerializer()
    BuildingCode = OrangeButtonSerializer()
    BuildingCodeNotes = OrangeButtonSerializer()
    ElectricCode = OrangeButtonSerializer()
    ElectricCodeNotes = OrangeButtonSerializer()
    FireCode = OrangeButtonSerializer()
    FireCodeNotes = OrangeButtonSerializer()
    ResidentialCode = OrangeButtonSerializer()
    ResidentialCodeNotes = OrangeButtonSerializer()
    WindCode = OrangeButtonSerializer()
    WindCodeNotes = OrangeButtonSerializer()
    Address = AddressSerializer(source='AddressID')
    Contacts = ContactSerializer(source='get_contacts', many=True)
    UnconfirmedContacts = ContactSerializer(source='get_unconfirmed',many=True)
    UnconfirmedInspections = AHJInspectionSerializer(source='get_unconfirmed_inspections', many=True)
    Polygon = PolygonSerializer(source='PolygonID')
    Comments = CommentSerializer(source='get_comments', many=True)
    AHJInspections = AHJInspectionSerializer(source='get_inspections', many=True)
    DocumentSubmissionMethods = DocumentSubmissionMethodUseSerializer(source='get_document_submission_methods', many=True)
    UnconfirmedDocumentSubmissionMethods = DocumentSubmissionMethodUseSerializer(source='get_uncon_dsm',many=True)
    PermitIssueMethods = PermitIssueMethodUseSerializer(source='get_permit_submission_methods', many=True)
    UnconfirmedPermitIssueMethods = PermitIssueMethodUseSerializer(source='get_uncon_pim',many=True)
    EngineeringReviewRequirements = EngineeringReviewRequirementSerializer(source='get_err',many=True)
    UnconfirmedEngineeringReviewRequirements = EngineeringReviewRequirementSerializer(source='get_uncon_err',many=True)
    FeeStructures = FeeStructureSerializer(source='get_fee_structures', many=True)
    UnconfirmedFeeStructures = FeeStructureSerializer(source='get_uncon_fs',many=True)


    def __init__(self, *args: Any, **kwargs: Any):
        fields_to_drop = []

        # Including extra context: https://www.django-rest-framework.org/api-guide/serializers/#including-extra-context
        # check if was provided to serializer context
        # not all views will provide the same context
        if 'fields_to_drop' in kwargs['context']:
            fields_to_drop = kwargs['context'].pop('fields_to_drop')
        super(AHJSerializer, self).__init__(*args, **kwargs)
        for field in fields_to_drop:
            self.fields.pop(field)

class EditSerializer(serializers.Serializer):
    EditID = serializers.IntegerField(read_only=True)
    ChangedBy = UserSerializer()
    ApprovedBy = UserSerializer()
    AHJPK = OrangeButtonSerializer()
    SourceTable = serializers.CharField()
    SourceColumn = serializers.CharField()
    SourceRow = serializers.IntegerField()
    ReviewStatus = serializers.CharField()
    Comments = serializers.CharField(allow_blank=True)
    OldValue = serializers.CharField(read_only=True)
    NewValue = serializers.CharField()
    DateRequested = serializers.DateField(read_only=True)
    DateEffective = serializers.DateField(read_only=True)
    AHJPK = serializers.IntegerField()
    Inspection = AHJInspectionSerializer(source='InspectionID')

    def create(self):
        # TODO: get edited row's old value
        return Edit(**self.validated_data)


class WebpageTokenSerializer(serializers.Serializer):
    auth_token = serializers.CharField(source='key')
    User = UserSerializer(source='get_user')


def dictfetchone(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    if row is None:
        return dict(zip(columns, [0] * len(columns)))
    return dict(zip(columns, row))


def get_polygons_in_state(statepolygonid):
    query = 'SELECT COUNT(*) as numAHJs,' +\
            'SUM(BuildingCode!="") as numBuildingCodes,' +\
            'SUM(ElectricCode!="") as numElectricCodes,' +\
            'SUM(FireCode!="") as numFireCodes,' +\
            'SUM(ResidentialCode!="") as numResidentialCodes,' + \
            'SUM(WindCode!="") as numWindCodes' + \
            ' FROM Polygon JOIN (SELECT PolygonID FROM CountyPolygon WHERE StatePolygonID=' \
            + statepolygonid + \
            ' UNION SELECT PolygonID FROM CityPolygon WHERE StatePolygonID=' \
            + statepolygonid + \
            ' UNION SELECT PolygonID FROM CountySubdivisionPolygon WHERE StatePolygonID=' \
            + statepolygonid + \
            ') as polygons_of_state ON Polygon.PolygonID=polygons_of_state.PolygonID LEFT JOIN AHJ ON Polygon.PolygonID=AHJ.PolygonID;'
    cursor = connection.cursor()
    cursor.execute(query)
    return dictfetchone(cursor)


class DataVisAHJPolygonInfoSerializer(serializers.Serializer):
    PolygonID = serializers.IntegerField()
    InternalPLatitude = serializers.DecimalField(max_digits=9, decimal_places=7)
    InternalPLongitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    Name = serializers.CharField()
    AHJPK = serializers.IntegerField()

    def to_representation(self, instance):
        # print(instance)
        r = OrderedDict(instance)
        if self.context.get('is_state', False) is True:
            r.update(get_polygons_in_state(str(r['PolygonID'])))
            # print(r)
        return r



