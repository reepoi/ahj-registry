from collections import OrderedDict

from django.db import connection
from rest_framework import serializers
from rest_framework_gis import serializers as geo_serializers
from djoser.serializers import UserCreateSerializer
from .models import *


class PolygonSerializer(geo_serializers.GeoFeatureModelSerializer):
    """
    Class to serialize Polygon objects into GeoJSON format
    plus extra properties in the properties section of
    the GeoJSON
    """
    AHJID = serializers.SerializerMethodField()

    class Meta:
        model = Polygon
        geo_field = 'Polygon'
        id_field = False
        fields = ['AHJID', 'LandArea', 'GEOID', 'InternalPLatitude', 'InternalPLongitude']

    def get_AHJID(self, instance):
        return self.context.get('AHJID', '')


class OrangeButtonSerializer(serializers.Field):
    """
    Custom serializer to add the Orange Button
    primitives to each field.
    "<field_name>": {
        "Value": "<value>,
        ...
    }
    """
    def get_attribute(self, instance):
        """
        Overridden method for correctly adding
        Orange Button primitives even when the
        field's value is null
        Otherwise, this class' to_representation
        will not be called by the caller serializer
        """
        attribute = super().get_attribute(instance)
        if attribute is None:
            return {'Value': None}
        else:
            return attribute

    def to_representation(self, value):
        """
        Method to take a field value and wrap
        it into Orange Button primitives
        """
        if type(value) is dict and 'Value' in value:
            return value
        ob_obj = {}
        ob_obj['Value'] = value
        return ob_obj


class FeeStructureSerializer(serializers.Serializer):
    """
    Serializes Orange Button FeeStrucuture object to OrderedDict
    """
    FeeStructurePK = OrangeButtonSerializer()
    FeeStructureID = OrangeButtonSerializer()
    FeeStructureName = OrangeButtonSerializer()
    FeeStructureType = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    FeeStructureStatus = OrangeButtonSerializer()

    def to_representation(self, feestructure):
        """
        Returns an OrderedDict representing an FeeStructure object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            for field in FeeStructure.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(feestructure)


class LocationSerializer(serializers.Serializer):
    """
    Serializes Orange Button Location object to OrderedDict
    """
    LocationID = OrangeButtonSerializer()
    Altitude = OrangeButtonSerializer()
    Elevation = OrangeButtonSerializer()
    Latitude = OrangeButtonSerializer()
    Longitude = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    LocationDeterminationMethod = OrangeButtonSerializer()
    LocationType = OrangeButtonSerializer()

    def to_representation(self, location):
        """
        Returns an OrderedDict representing an Location object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            for field in Location.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(location)


class AddressSerializer(serializers.Serializer):
    """
    Serializes Orange Button Address object to OrderedDict
    """
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

    def to_representation(self, address):
        """
        Returns an OrderedDict representing an Address object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            for field in Address.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(address)


class ContactSerializer(serializers.Serializer):
    """
    Serializes Orange Button Contact object to OrderedDict
    """
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

    def to_representation(self, contact):
        """
        Returns an OrderedDict representing an Contact object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            for field in Contact.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(contact)


class RecursiveField(serializers.Serializer):
    """
    Serializer that calls the caller serializer on the value
    of the field that was passed to it.
    Used for serializing Comments
    """
    def to_representation(self, value):
        """
        Calls the caller serializer that called this serializer
        """
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class SubscribedChannelsSerializer(serializers.Serializer):
    """
    Serializes SubscribedChannel to OrderedDict
    """
    RoomID = serializers.IntegerField(source='id')
    ChannelID = serializers.CharField()
    LastReadToken = serializers.CharField()
    Users = serializers.ListField(source="get_participating_users")


class UserSerializer(serializers.Serializer):
    """
    Serializes User to OrderedDict
    """
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
    APICalls = serializers.IntegerField()
    SignUpDate = serializers.DateField()
    MaintainedAHJs = serializers.ListField(source='get_maintained_ahjs')
    ChatRooms = SubscribedChannelsSerializer(source="get_subscribed_channels", many=True)


class UserCreateSerializer(UserCreateSerializer):
    """
    Serializes User to Ordered Dict.
    Used when a new user is created.
    """
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('UserID', 'ContactID', 'Username', 'password', 'Email', 'is_staff', 'is_active', 'SignUpDate', 'PersonalBio', 'URL', 'CompanyAffiliation', 'Photo', 'IsPeerReviewer', 'NumReviewsDone', 'CommunityScore', 'APICalls', 'SecurityLevel')


class CommentSerializer(serializers.Serializer):
    """
    Serializes Comment to OrderedDict.
    """
    CommentID = OrangeButtonSerializer()
    User = UserSerializer(source='UserID')
    CommentText = OrangeButtonSerializer()
    Date = OrangeButtonSerializer()
    Replies = RecursiveField(source='get_replies', many=True)


class DocumentSubmissionMethodUseSerializer(serializers.Serializer):
    """
    Serializes Orange Button DocumentSubmissionMethod object value to OrderedDict
    """
    UseID = serializers.IntegerField()
    Value = serializers.CharField(source='get_value')


class PermitIssueMethodUseSerializer(serializers.Serializer):
    """
    Serializes Orange Button PermitIssueMethod object value to OrderedDict
    """
    UseID = serializers.IntegerField()
    Value = serializers.CharField(source='get_value')


class AHJInspectionSerializer(serializers.Serializer):
    """
    Serializes Orange Button AHJInspection object
    """
    InspectionID = OrangeButtonSerializer()
    InspectionType = OrangeButtonSerializer()
    AHJInspectionName = OrangeButtonSerializer()
    AHJInspectionNotes = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    FileFolderURL = OrangeButtonSerializer()
    TechnicianRequired = OrangeButtonSerializer()
    InspectionStatus = OrangeButtonSerializer()
    Contacts = ContactSerializer(source='get_contacts', many=True)
    UnconfirmedContacts = ContactSerializer(source='get_uncon_con', many=True)

    def to_representation(self, inspection):
        """
        Returns an OrderedDict representing an AHJInspection object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            for field in AHJInspection.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(inspection)


class EngineeringReviewRequirementSerializer(serializers.Serializer):
    """
    Serializes Orange Button EngineeringReviewRequirement object to OrderedDict
    """
    EngineeringReviewRequirementID = OrangeButtonSerializer()
    Description = OrangeButtonSerializer()
    EngineeringReviewType = OrangeButtonSerializer()
    RequirementLevel = OrangeButtonSerializer()
    RequirementNotes = OrangeButtonSerializer()
    StampType = OrangeButtonSerializer()
    EngineeringReviewRequirementStatus = OrangeButtonSerializer()

    def to_representation(self, err):
        """
        Returns an OrderedDict representing an EngineeringReviewRequirement object to OrderedDict
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            for field in EngineeringReviewRequirement.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(err)


class AHJSerializer(serializers.Serializer):
    """
    Serializes Orange Button AHJ object
    """
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
        """
        Returns an OrderedDict representing an AHJ object
        Note not every AHJ has every child object.
        If 'is_public_view' is True, will not serialize fields
        that are not meant for public api users.
        """
        if self.context.get('is_public_view', False):
            for field in AHJ.SERIALIZER_EXCLUDED_FIELDS:
                if field in self.fields:
                    self.fields.pop(field)
        return super().to_representation(ahj)

    def get_Polygon(self, instance):
        """
        Helper method to serialize the polygon associated with an AHJ
        """
        return PolygonSerializer(instance.PolygonID, context={'AHJID': instance.AHJID}).data


class EditSerializer(serializers.Serializer):
    """
    Serializes edits for the webpage AHJPage.
    """
    EditID = serializers.IntegerField(read_only=True)
    ChangedBy = UserSerializer()
    ApprovedBy = UserSerializer()
    AHJPK = serializers.IntegerField()
    SourceTable = serializers.CharField()
    SourceColumn = serializers.CharField()
    SourceRow = serializers.IntegerField()
    ReviewStatus = serializers.CharField()
    Comments = serializers.CharField(allow_blank=True)
    OldValue = serializers.CharField(read_only=True)
    NewValue = serializers.CharField()
    DateRequested = serializers.DateField(read_only=True)
    DateEffective = serializers.DateField(read_only=True)
    Inspection = AHJInspectionSerializer(source='InspectionID')

    def create(self):
        """
        Creates an edit object without saving to database
        """
        return Edit(**self.validated_data)


class WebpageTokenSerializer(serializers.Serializer):
    """
    Serializes webpage token and user info when a user logs
    into the webpage.
    """
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
    """
    Given a state polygon id, returns a dict containing various statistics as:
    {
        "numAHJs": <number_of_ahjs_in_state>,
        "numBuildingCodes": <number_of_ahjs_with_known_building_codes>,
        "numElectricCodes": <number_of_ahjs_with_known_electric_codes>,
        "numFireCodes": <number_of_ahjs_with_known_fire_codes>,
        "numResidentialCodes": <number_of_ahjs_with_known_residential_codes>,
        "numWindCodes": <number_of_ahjs_with_known_wind_codes>
    }
    """
    query = 'SELECT COUNT(*) as numAHJs,' + \
            'SUM(BuildingCode!="") as numBuildingCodes,' + \
            'SUM(ElectricCode!="") as numElectricCodes,' + \
            'SUM(FireCode!="") as numFireCodes,' + \
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
    """
    Serializes statistics about each state around their permit requirements.
    """
    PolygonID = serializers.IntegerField()
    InternalPLatitude = serializers.DecimalField(max_digits=9, decimal_places=7)
    InternalPLongitude = serializers.DecimalField(max_digits=10, decimal_places=7)
    Name = serializers.CharField()
    AHJPK = serializers.IntegerField()

    def to_representation(self, instance):
        """
        Returns a list of states plus all their permit requirement
        coverage stats across all administrative areas in the state.
        """
        r = OrderedDict(instance)
        if self.context.get('is_state', False) is True:
            r.update(get_polygons_in_state(str(r['PolygonID'])))
        return r
