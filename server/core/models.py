from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.core.exceptions import FieldDoesNotExist
from ahj_gis.models import Polygon
from django.apps import apps
import json
from taggit.managers import TaggableManager
from simple_history.models import HistoricalRecords
from django.utils import timezone
from .constants import *
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage

import uuid


def retrieve_edit(record, field_name, edit):
    if edit is None:
        if record.__class__.__name__ == 'AHJ':
            return Edit(RecordID=record.AHJID, RecordType='AHJ', Value=getattr(record, field_name), FieldName=field_name)
        elif record.__class__.__name__ == 'FeeStructure':
            return Edit(RecordID=record.FeeStructureID, RecordType='FeeStructure', Value=getattr(record, field_name), FieldName=field_name)
        return Edit(RecordID=record.id, RecordType=record.__class__.__name__, Value=getattr(record, field_name), FieldName=field_name)
    else:
        return edit


def get_edit(record, field_name, find_create_edit, confirmed_edits_only, highest_vote_rating):
    record_edits = get_all_record_edits(record)
    if find_create_edit:
        edit = record_edits.filter(EditType='create').first()
        return retrieve_edit(record, field_name, edit)

    record_edits_field_name = record_edits.filter(FieldName=field_name)
    if confirmed_edits_only:
        edit = record_edits_field_name.filter(IsConfirmed=True).order_by('-ConfirmedDate').first()
        return retrieve_edit(record, field_name, edit)
    elif highest_vote_rating:
        edits = record_edits_field_name.filter(IsConfirmed=None).order_by('-VoteRating')
        if len(edits) > 1:
            highest_vote = edits.first().VoteRating
            edits = edits.filter(VoteRating=highest_vote)
            edit = edits.order_by('-ModifiedDate').first()
        else:
            edit = edits.first()
        if edit is None:
            return get_edit(record, field_name, False, True, False)
        return retrieve_edit(record, field_name, edit)
    else:
        edit = record_edits_field_name.order_by('-ModifiedDate').first()
        if edit is not None and edit.IsConfirmed:
            return get_edit(record, field_name, False, True, False)
        return retrieve_edit(record, field_name, edit)


def add_delete_edits(record, edit):
    # The record will never be an AHJ record
    if record.__class__.__name__ == 'FeeStructure':
        record_id = record.FeeStructureID
    else:
        record_id = record.id
    Edit.objects.create(RecordID=record_id, RecordType=record.__class__.__name__, EditType='delete',
                        ModifyingUserID=edit.ModifyingUserID,
                        ModifiedDate=edit.ModifiedDate, IsConfirmed=True, ConfirmingUserID=edit.ConfirmingUserID,
                        ConfirmedDate=edit.ConfirmedDate)


def get_all_record_edits(record):
    if record.__class__.__name__ == 'AHJ':
        return Edit.objects.filter(RecordID=record.AHJID)
    elif record.__class__.__name__ == 'FeeStructure':
        return Edit.objects.filter(RecordID=record.FeeStructureID)
    return Edit.objects.filter(RecordID=record.id).filter(RecordType=record.__class__.__name__)


def reject_all_unconfirmed_record_update_edits(record, edit):
    record_edits = get_all_record_edits(record).filter(IsConfirmed=None).filter(EditType='update')
    for record_edit in record_edits:
        record_edit.reject(edit.ConfirmingUserID)


def check_record_edit_create_confirmed(record):
    if record.__class__.__name__ == 'AHJ':
        create_edit = Edit.objects.filter(RecordID=record.AHJID).filter(RecordType=record.__class__.__name__).filter(EditType='create').first()
    elif record.__class__.__name__ == 'FeeStructure':
        create_edit = Edit.objects.filter(RecordID=record.FeeStructureID).filter(RecordType=record.__class__.__name__).filter(EditType='create').first()
    else:
        create_edit = Edit.objects.filter(RecordID=record.id).filter(RecordType=record.__class__.__name__).filter(EditType='create').first()
    if create_edit is None or create_edit.IsConfirmed:
        return True
    return False


class AHJ(models.Model):
    mpoly = models.ForeignKey(Polygon, null=True, on_delete=models.DO_NOTHING)
    AHJCode = models.CharField(blank=True, max_length=20)
    AHJID = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    AHJLevelCode = models.CharField(blank=True, max_length=3)
    AHJName = models.CharField(blank=True, max_length=100)
    BuildingCode = models.CharField(choices=BUILDING_CODE_CHOICES, blank=True, default='', max_length=45)
    BuildingCodeNotes = models.CharField(blank=True, max_length=255)
    DataSourceComments = models.TextField(blank=True)
    Description = models.TextField(blank=True)
    DocumentSubmissionMethodNotes = models.CharField(blank=True, max_length=255)
    ElectricCode = models.CharField(choices=ELECTRIC_CODE_CHOICES, blank=True, default='', max_length=45)
    ElectricCodeNotes = models.CharField(blank=True, max_length=255)
    EstimatedTurnaroundDays = models.IntegerField(null=True)
    FileFolderURL = models.CharField(blank=True, max_length=255)
    FireCode = models.CharField(choices=FIRE_CODE_CHOICES, blank=True, default='', max_length=45)
    FireCodeNotes = models.CharField(blank=True, max_length=255)
    PermitIssueMethodNotes = models.CharField(blank=True, max_length=255)
    ResidentialCode = models.CharField(choices=RESIDENTIAL_CODE_CHOICES, blank=True, default='', max_length=45)
    ResidentialCodeNotes = models.CharField(blank=True, max_length=255)
    URL = models.CharField(blank=True, max_length=255)
    WindCode = models.CharField(choices=WIND_CODE_CHOICES, blank=True, default='', max_length=45)
    WindCodeNotes = models.CharField(blank=True, max_length=255)
    history = HistoricalRecords()

    edit_set = None

    def get_ahj(self):
        return self

    def get_edit(self, field_name, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name=field_name, find_create_edit=False, confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def get_create_edit(self, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name='AHJID', find_create_edit=True,  confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def chain_delete(self, edit):
        address = Address.objects.filter(AHJ=self).first()
        if address is not None:
            address.chain_delete(edit)
        contacts = Contact.objects.filter(AHJ=self)
        for contact in contacts:
            contact.chain_delete(edit)
        eng_rev_reqs = EngineeringReviewRequirement.objects.filter(AHJ=self)
        for eng_rev_req in eng_rev_reqs:
            eng_rev_req.chain_delete(edit)
        ahj_inspections = AHJInspection.objects.filter(AHJ=self)
        for ahj_inspection in ahj_inspections:
            ahj_inspection.chain_delete(edit)
        fee_structures = FeeStructure.objects.filter(AHJ=self)
        for fee_structure in fee_structures:
            fee_structure.chain_delete(edit)
        doc_sub_methods = DocumentSubmissionMethod.objects.filter(AHJ=self)
        for doc_sub_method in doc_sub_methods:
            doc_sub_method.chain_delete(edit)
        permit_issue_methods = PermitIssueMethod.objects.filter(AHJ=self)
        for permit_issue_method in permit_issue_methods:
            permit_issue_method.chain_delete(edit)
        if edit.IsConfirmed is False:
            reject_all_unconfirmed_record_update_edits(self, edit)
        self.delete()


class DocumentSubmissionMethod(models.Model):
    AHJ = models.ForeignKey(AHJ, to_field='AHJID', null=True, on_delete=models.CASCADE)
    DocumentSubmissionMethod = models.CharField(choices=DOCUMENT_SUBMISSION_METHOD_CHOICES, blank=True, default='', max_length=45)

    def get_ahj(self):
        return self.AHJ

    def get_edit(self, field_name, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name=field_name, find_create_edit=False, confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def get_create_edit(self, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name='id', find_create_edit=True,  confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def chain_delete(self, edit):
        if edit.IsConfirmed:
            add_delete_edits(self, edit)
        elif edit.IsConfirmed is False:
            reject_all_unconfirmed_record_update_edits(self, edit)
        self.delete()


class PermitIssueMethod(models.Model):
    AHJ = models.ForeignKey(AHJ, to_field='AHJID', null=True, on_delete=models.CASCADE)
    PermitIssueMethod = models.CharField(choices=PERMIT_ISSUE_METHOD_CHOICES, blank=True, default='', max_length=45)

    def get_ahj(self):
        return self.AHJ

    def get_edit(self, field_name, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name=field_name, find_create_edit=False, confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def get_create_edit(self, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name='id', find_create_edit=True,  confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def chain_delete(self, edit):
        if edit.IsConfirmed:
            add_delete_edits(self, edit)
        elif edit.IsConfirmed is False:
            reject_all_unconfirmed_record_update_edits(self, edit)
        self.delete()


class AHJInspection(models.Model):
    AHJ = models.ForeignKey(AHJ, to_field='AHJID', null=True, on_delete=models.CASCADE)
    AHJInspectionName = models.CharField(blank=True, max_length=100)
    AHJInspectionNotes = models.CharField(blank=True, max_length=255)
    Description = models.TextField(blank=True)
    FileFolderURL = models.CharField(blank=True, max_length=255)
    InspectionType = models.CharField(choices=INSPECTION_TYPE_CHOICES, blank=True, default='', max_length=45)
    TechnicianRequired = models.BooleanField(null=True)

    def get_ahj(self):
        return self.AHJ

    def get_edit(self, field_name, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name=field_name, find_create_edit=False, confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def get_create_edit(self, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name='id', find_create_edit=True,  confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def chain_delete(self, edit):
        contacts = Contact.objects.filter(AHJInspection=self)
        for contact in contacts:
            contact.chain_delete(edit)
        if edit.IsConfirmed:
            add_delete_edits(self, edit)
        elif edit.IsConfirmed is False:
            reject_all_unconfirmed_record_update_edits(self, edit)
        self.delete()


class Contact(models.Model):
    AHJ = models.ForeignKey(AHJ, to_field='AHJID', null=True, on_delete=models.CASCADE)
    AHJInspection = models.ForeignKey(AHJInspection, to_field='id', null=True, on_delete=models.CASCADE)
    ContactTimezone = models.CharField(blank=True, max_length=100)
    ContactType = models.CharField(choices=CONTACT_TYPE_CHOICES, blank=True, default='', max_length=45)
    Description = models.TextField(blank=True)
    Email = models.CharField(blank=True, max_length=100)
    FirstName = models.CharField(blank=True, max_length=100)
    HomePhone = models.CharField(blank=True, max_length=31)
    LastName = models.CharField(blank=True, max_length=100)
    MiddleName = models.CharField(blank=True, max_length=100)
    MobilePhone = models.CharField(blank=True, max_length=31)
    PreferredContactMethod = models.CharField(choices=PREFERRED_CONTACT_METHOD_CHOICES, blank=True, default='', max_length=45)
    Title = models.CharField(blank=True, max_length=100)
    URL = models.CharField(blank=True, max_length=255)
    WorkPhone = models.CharField(blank=True, max_length=31)
    history = HistoricalRecords()

    def get_ahj(self):
        if self.AHJ is None:
            return self.AHJInspection.get_ahj()
        return self.AHJ

    def get_edit(self, field_name, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name=field_name, find_create_edit=False, confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def get_create_edit(self, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name='id', find_create_edit=True,  confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def chain_delete(self, edit):
        address = Address.objects.filter(Contact=self).first()
        if address is not None:
            address.chain_delete(edit)
        if edit.IsConfirmed:
            add_delete_edits(self, edit)
        elif edit.IsConfirmed is False:
            reject_all_unconfirmed_record_update_edits(self, edit)
        self.delete()


class EngineeringReviewRequirement(models.Model):
    AHJ = models.ForeignKey(AHJ, to_field='AHJID', null=True, on_delete=models.CASCADE)
    Description = models.TextField(blank=True)
    EngineeringReviewType = models.CharField(choices=ENGINEERING_REVIEW_TYPE_CHOICES, blank=True, default='', max_length=45)
    RequirementLevel = models.CharField(choices=REQUIREMENT_LEVEL_CHOICES, blank=True, default='', max_length=45)
    RequirementNotes = models.CharField(blank=True, max_length=255)
    StampType = models.CharField(choices=STAMP_TYPE_CHOICES, max_length=45)
    history = HistoricalRecords()

    def get_ahj(self):
        return self.AHJ

    def get_edit(self, field_name, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name=field_name, find_create_edit=False, confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def get_create_edit(self, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name='id', find_create_edit=True,  confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def chain_delete(self, edit):
        if edit.IsConfirmed:
            add_delete_edits(self, edit)
        elif edit.IsConfirmed is False:
            reject_all_unconfirmed_record_update_edits(self, edit)
        self.delete()


class Address(models.Model):
    AHJ = models.OneToOneField(AHJ, to_field='AHJID', null=True, blank=True, on_delete=models.CASCADE)
    Contact = models.OneToOneField(Contact, null=True, blank=True, on_delete=models.CASCADE)
    AddrLine1 = models.CharField(blank=True, max_length=100)
    AddrLine2 = models.CharField(blank=True, max_length=100)
    AddrLine3 = models.CharField(blank=True, max_length=100)
    AddressType = models.CharField(choices=ADDRESS_TYPE_CHOICES, blank=True, default='', max_length=45)
    City = models.CharField(blank=True, max_length=100)
    Country = models.CharField(blank=True, max_length=100)
    County = models.CharField(blank=True, max_length=100)
    Description = models.TextField(blank=True)
    StateProvince = models.CharField(blank=True, max_length=100)
    ZipPostalCode = models.CharField(blank=True, max_length=10)
    history = HistoricalRecords()

    def get_ahj(self):
        if self.AHJ is None:
            return self.Contact.get_ahj()
        return self.AHJ

    def get_edit(self, field_name, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name=field_name, find_create_edit=False, confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def get_create_edit(self, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name='id', find_create_edit=True,  confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def chain_delete(self, edit):
        location = Location.objects.filter(Address=self).first()
        if location is not None:
            location.chain_delete(edit)
        if edit.IsConfirmed:
            add_delete_edits(self, edit)
        elif edit.IsConfirmed is False:
            reject_all_unconfirmed_record_update_edits(self, edit)
        self.delete()


class Location(models.Model):
    Address = models.OneToOneField(Address, on_delete=models.CASCADE)
    Altitude = models.DecimalField(null=True, max_digits=15, decimal_places=6)
    Description = models.TextField(blank=True)
    Elevation = models.DecimalField(null=True, max_digits=15, decimal_places=6)
    Latitude = models.DecimalField(null=True, max_digits=8, decimal_places=6)
    LocationDeterminationMethod = models.CharField(choices=LOCATION_DETERMINATION_METHOD_CHOICES, blank=True, default='', max_length=45)
    LocationType = models.CharField(choices=LOCATION_TYPE_CHOICES, blank=True, default='', max_length=45)
    Longitude = models.DecimalField(null=True, max_digits=9, decimal_places=6)
    history = HistoricalRecords()

    def get_ahj(self):
        return self.Address.get_ahj()

    def get_edit(self, field_name, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name=field_name, find_create_edit=False, confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def get_create_edit(self, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name='id', find_create_edit=True,  confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def chain_delete(self, edit):
        if edit.IsConfirmed:
            add_delete_edits(self, edit)
        elif edit.IsConfirmed is False:
            reject_all_unconfirmed_record_update_edits(self, edit)
        self.delete()


class FeeStructure(models.Model):
    AHJ = models.ForeignKey(AHJ, to_field='AHJID', null=True, on_delete=models.CASCADE)
    Description = models.TextField(blank=True)
    FeeStructureID = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    FeeStructureName = models.CharField(blank=True, max_length=100)
    FeeStructureType = models.CharField(choices=FEE_STRUCTURE_TYPE_CHOICES, blank=True, default='', max_length=45)
    history = HistoricalRecords()

    def get_ahj(self):
        return self.AHJ

    def get_edit(self, field_name, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name=field_name, find_create_edit=False, confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def get_create_edit(self, confirmed_edits_only, highest_vote_rating):
        return get_edit(record=self, field_name='FeeStructureID', find_create_edit=True,  confirmed_edits_only=confirmed_edits_only, highest_vote_rating=highest_vote_rating)

    def chain_delete(self, edit):
        if edit.IsConfirmed:
            add_delete_edits(self, edit)
        elif edit.IsConfirmed is False:
            reject_all_unconfirmed_record_update_edits(self, edit)
        self.delete()


# Authentication and Authorization
# Create an auth token every time a user is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def send_user_confirmation_email(user):
    subject = 'AHJ Registry - Activate your account'
    message = render_to_string('acc_active_email.html', {
        'user': user,
        'domain': settings.EMAIL_LINK_DOMAIN,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': user.email_confirmation_token.make_token(user)
    })
    email = EmailMessage(subject, message, to=[user.email_address])
    email.content_subtype = 'html'
    email.send()


def send_edit_confirmation_email(user, edit):
    subject = 'AHJ Registry - An edit was submitted.'
    message = render_to_string('confirm_reject_edit_email.html', {
        'user': user,
        'domain': settings.EMAIL_LINK_DOMAIN,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': user.email_confirmation_token.make_token(user),
        'edit': edit,
        'ahj': edit.get_record().get_ahj()
    })
    email = EmailMessage(subject, message, to=[user.email_address])
    email.content_subtype = 'html'
    email.send()


class EmailConfirmationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email_address, password, **extra_fields):
        if not email_address:
            raise ValueError('The given email_address must be set')
        email_address = self.normalize_email(email_address)
        user = self.model(email_address=email_address, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email_address, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email_address, password, **extra_fields)

    def create_superuser(self, email_address, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email_address, password, **extra_fields)


class User(AbstractBaseUser):
    identifier = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email_address = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    AHJ = models.ManyToManyField(AHJ)

    # FK one to many
    # entity = models.ForeignKey(Entity, on_delete=models.CASCADE, blank=True, null=True)

    objects = UserManager()
    email_confirmation_token = EmailConfirmationTokenGenerator()

    USERNAME_FIELD = 'email_address'
    EMAIL_FIELD = 'email_address'

    def __str__(self):
        return self.email_address

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, core):
        return self.is_superuser

    @property
    def is_staff(self):
        return self.is_superuser

    tags = TaggableManager()


class Edit(models.Model):
    RecordID = models.CharField(max_length=45)
    RecordType = models.CharField(max_length=45)
    ParentID = models.CharField(default='', max_length=45)
    ParentRecordType = models.CharField(default='', max_length=45)
    EditType = models.CharField(max_length=45)
    FieldName = models.CharField(default='', max_length=45)
    Value = models.TextField(default=None, null=True)
    PreviousValue = models.TextField(default=None, null=True)
    ModifyingUserID = models.IntegerField()
    ModifiedDate = models.DateTimeField(auto_now_add=True)
    IsConfirmed = models.BooleanField(null=True, default=None)
    ConfirmingUserID = models.IntegerField(null=True, default=None)
    ConfirmedDate = models.DateTimeField(null=True, default=None)
    VoteRating = models.IntegerField(default=0)

    def get_record_owners(self):
        return User.objects.filter(AHJ=self.get_record().get_ahj())

    def is_record_owner(self, user_id):
        owners = self.get_record_owners()
        for owner in owners:
            if user_id == owner.id:
                return True
        return False

    def create_record(self):
        if self.RecordType == 'AHJ':
            record = AHJ.objects.create()
            self.RecordID = record.AHJID
        elif self.RecordType == 'FeeStructure':
            if self.RecordID != '':
                FeeStructure.objects.create(**{'FeeStructureID': self.RecordID, self.ParentRecordType: self.get_parent()})
            else:
                record = FeeStructure.objects.create(**{self.ParentRecordType: self.get_parent()})
                self.RecordID = record.FeeStructureID
        else:
            record = apps.get_model('core', self.RecordType).objects.create(**{self.ParentRecordType: self.get_parent()})
            self.RecordID = record.id
        self.Value = self.RecordID
        self.save()

    def get_parent(self):
        if self.ParentRecordType == 'AHJ':
            return apps.get_model('core', self.ParentRecordType).objects.filter(AHJID=self.ParentID).first()
        elif self.ParentRecordType == 'FeeStructure':
            return apps.get_model('core', self.ParentRecordType).objects.filter(FeeStructureID=self.ParentID).first()
        return apps.get_model('core', self.ParentRecordType).objects.filter(id=self.ParentID).first()

    def get_record(self):
        if self.RecordType == 'AHJ':
            record = AHJ.objects.filter(AHJID=self.RecordID).first()
        elif self.RecordType == 'FeeStructure':
            record = FeeStructure.objects.filter(FeeStructureID=self.RecordID).first()
        else:
            record = apps.get_model('core', self.RecordType).objects.filter(id=self.RecordID).first()
        return record

    def get_record_query_set(self):
        if self.RecordType == 'AHJ':
            record = AHJ.objects.filter(AHJID=self.RecordID)
        elif self.RecordType == 'FeeStructure':
            record = FeeStructure.objects.filter(FeeStructureID=self.RecordID)
        else:
            record = apps.get_model('core', self.RecordType).objects.filter(id=self.RecordID)
        return record

    def get_user_confirm(self):
        return User.objects.filter(pk=self.ConfirmingUserID).first()

    def get_user_modify(self):
        return User.objects.filter(pk=self.ModifyingUserID).first()

    def accept(self, user_id):
        if self.EditType == 'create':
            if self.RecordType != 'AHJ':
                parent = self.get_parent()
                if not check_record_edit_create_confirmed(parent):
                    return
        elif self.EditType == 'update':
            record_query_set = self.get_record_query_set()
            if record_query_set.exists():
                if not check_record_edit_create_confirmed(record_query_set.first()):
                    self.save()
                    return
                field_update = {self.FieldName: self.Value}
                record_query_set.update(**field_update)
        elif self.EditType == 'delete':
            self.IsConfirmed = True
            self.ConfirmingUserID = user_id
            self.ConfirmedDate = timezone.now()
            self.get_record().chain_delete(self)
            self.save()
            return
        self.IsConfirmed = True
        self.ConfirmingUserID = user_id
        self.ConfirmedDate = timezone.now()
        self.save()

    def reject(self, user_id):
        if self.EditType == 'create':
            self.get_record().chain_delete(self)
        self.IsConfirmed = False
        self.ConfirmingUserID = user_id
        self.ConfirmedDate = timezone.now()
        self.save()

    def validate_RecordType(self):
        try:
            apps.get_model('core', self.RecordType)
            return True
        except LookupError:
            return False

    def validate_ParentRecordType(self):
        try:
            apps.get_model('core', self.RecordType)
            return True
        except LookupError:
            return False

    def validate_FieldName(self):
        record_meta = apps.get_model('core', self.RecordType)._meta
        try:
            field_name = record_meta.get_field(self.FieldName).__class__.__name__
            if field_name == 'id' or field_name == 'AHJID' or field_name == 'ForeignKey' or field_name == 'OneToOneField':
                return False
            return True
        except FieldDoesNotExist:
            return False

    def clean_Value(self):
        record_field_meta = apps.get_model('core', self.RecordType)._meta.get_field(self.FieldName)
        choices_dict = dict(record_field_meta.choices)
        if choices_dict:
            choices_dict[''] = ''
            if self.Value not in choices_dict:
                return False
        if record_field_meta.__class__.__name__ == 'DecimalField':
            if self.Value == '':
                self.Value = None
                return True
            try:
                float(self.Value)
            except ValueError:
                return False
        if self.RecordType in FIELD_VALIDATION:
            if self.FieldName in FIELD_VALIDATION[self.RecordType]:
                if not FIELD_VALIDATION[self.RecordType][self.FieldName](self.Value):
                    return False
        return True

    def set_vote_rating(self):
        votes = Vote.objects.filter(Edit=self)
        upvotes = len(votes.filter(Rating=True))
        downvotes = len(votes.filter(Rating=False))
        vote_update = {'VoteRating': upvotes - downvotes}
        Edit.objects.filter(pk=self.id).update(**vote_update)


class Vote(models.Model):
    Edit = models.ForeignKey(Edit, on_delete=models.DO_NOTHING)
    VotingUserID = models.IntegerField()
    Rating = models.BooleanField()

    def get_user(self):
        return User.objects.filter(pk=self.VotingUserID).first()
