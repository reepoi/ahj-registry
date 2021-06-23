import datetime

from django.apps import apps
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .authentication import WebpageTokenAuth
from .models import AHJ, Edit, AHJUserMaintains
from .serializers import AHJSerializer, EditSerializer, ContactSerializer, \
    EngineeringReviewRequirementSerializer, PermitIssueMethodUseSerializer, DocumentSubmissionMethodUseSerializer, \
    FeeStructureSerializer, AHJInspectionSerializer
from .usf import ENUM_FIELDS, get_enum_value_row


def add_edit(edit_dict: dict, ReviewStatus='P', ApprovedBy=None, DateEffective=None):
    """
    Saves a new edit given a dict with these key-value pairs.
    The kwargs allow saving an approved or rejected edit.
    """
    edit = Edit()
    edit.ChangedBy = edit_dict.get('User')
    edit.DateRequested = timezone.now()
    edit.AHJPK = edit_dict.get('AHJPK')
    edit.SourceTable = edit_dict.get('SourceTable')
    edit.SourceColumn = edit_dict.get('SourceColumn')
    edit.SourceRow = edit_dict.get('SourceRow')
    edit.OldValue = edit_dict.get('OldValue')
    edit.NewValue = edit_dict.get('NewValue')
    edit.ReviewStatus = ReviewStatus
    if ReviewStatus == 'A':
        edit.ApprovedBy = ApprovedBy
        edit.DateEffective = DateEffective
    edit.EditType = edit_dict.get('EditType')
    edit.save()
    return edit


def apply_edits(ready_edits=None):
    """
    Applies the changes of a list of edits.
    If a list is not provided, it applies all edits whose DateEffective is today.
    For rejected edit additions, this sets the SourceColumn of the edited row to False.
    """
    if ready_edits is None:
        ready_edits = Edit.objects.filter(
            ReviewStatus='A',
            DateEffective__date=datetime.date.today()
        ).exclude(ApprovedBy=None)
    for edit in ready_edits:
        row = edit.get_edited_row()
        if edit.SourceColumn in ENUM_FIELDS:
            if edit.NewValue == '':
                new_value = None
            else:
                new_value = get_enum_value_row(edit.SourceColumn, edit.NewValue)
        else:
            new_value = edit.NewValue
        setattr(row, edit.SourceColumn, new_value)
        row.save()

    # If an addition edit is rejected, set its status false
    # rejected_addition_edits = Edit.objects.filter(
    #     ReviewStatus='R',
    #     EditType='A',
    #     DateEffective__date=datetime.date.today()
    # ).exclude(ApprovedBy=None)
    # for edit in rejected_addition_edits:
    #     row = edit.get_edited_row()
    #     setattr(row, row.get_relation_status_field(), False)
    #     row.save()


def revert_edit(user, edit):
    """
    Creates and applies an edit that reverses the change of the given edit.
    The OldValue of the created edit is the current value of the edited field.
    """
    if edit.ReviewStatus == 'P':
        return
    row = edit.get_edited_row()
    current_value = getattr(row, edit.SourceColumn)
    if edit.SourceColumn in ENUM_FIELDS:
        current_value = current_value.Value if current_value is not None else ''
    if edit.EditType in {'A', 'D'}:
        next_value = not edit.NewValue
    else:
        next_value = edit.OldValue
    if current_value == next_value:
        return
    revert_edit_dict = {'User': user,
                        'AHJPK': edit.AHJPK,
                        'SourceTable': edit.SourceTable,
                        'SourceColumn': edit.SourceColumn,
                        'SourceRow': edit.SourceRow,
                        'OldValue': current_value,
                        'NewValue': next_value,
                        'EditType': edit.EditType}
    e = add_edit(revert_edit_dict, ReviewStatus='A', ApprovedBy=user, DateEffective=timezone.now())
    apply_edits(ready_edits=[e])


def edit_is_applied(edit):
    """
    Determines if an edit has been approved and applied.
    Edits are applied if their ReviewStatus is 'A' for approved,
    and if their DateEffective has passed.
    """
    edit_is_approved = edit.ReviewStatus == 'A'
    date_effective_passed = edit.DateEffective is not None and edit.DateEffective.date() <= timezone.now().date()
    return edit_is_approved and date_effective_passed


def edit_is_resettable(edit):
    """
    Determines if an edit can be reset. To be resettable, it must either be:
     - Rejected.
     - Approved, but whose changes have not been applied to the edited row.
     - Approved and applied, but no other edits have been applied after it.
    """
    is_rejected = edit.ReviewStatus == 'R'
    is_applied = edit_is_applied(edit)
    is_approved_not_applied = edit.ReviewStatus == 'A' and not is_applied
    is_latest_applied = is_applied and not Edit.objects.filter(SourceTable=edit.SourceTable, SourceRow=edit.SourceRow, SourceColumn=edit.SourceColumn,
                                                               ReviewStatus='A', DateEffective__gt=edit.DateEffective).exists()
    return is_rejected or is_approved_not_applied or is_latest_applied


def edit_make_pending(edit):
    """
    Sets an edit to a pending approval or rejection state.
    """
    edit.ReviewStatus = 'P'
    edit.ApprovedBy = None
    edit.DateEffective = None
    edit.save()


def edit_update_old_value(edit):
    """
    Updates the OldValue of an edit to the current value of
    the SourceColumn of the edited row.
    """
    row = edit.get_edited_row()
    current_value = getattr(row, edit.SourceColumn)
    if edit.SourceColumn in ENUM_FIELDS:
        current_value = current_value.Value if current_value is not None else ''
    edit.OldValue = current_value
    edit.save()


def edit_undo_apply(edit):
    """
    Sets the SourceColumn of the edited row to
    the OldValue of the edit.
    """
    row = edit.get_edited_row()
    if edit.SourceColumn in ENUM_FIELDS:
        if edit.OldValue == '':
            value = None
        else:
            value = get_enum_value_row(edit.SourceColumn, edit.OldValue)
    else:
        value = edit.OldValue
    setattr(row, edit.SourceColumn, value)
    row.save()


def reset_edit(user, edit, force_resettable=False, skip_undo=False):
    """
    Rolls back the an edit in a similar way to Git's 'git reset' command.
    When an edit is reset, it returns to a pending state, again awaiting
    approval or rejection. If the edit was applied already, its changes
    to the edited row are undone.
    If an edit is not resettable, it is instead reverted.
    """
    if edit_is_resettable(edit) or force_resettable:
        if edit_is_applied(edit) and not skip_undo:
            edit_undo_apply(edit)
        else:
            edit_update_old_value(edit)
        edit_make_pending(edit)
    elif edit.ReviewStatus == 'A':
        revert_edit(user, edit)

####################

@api_view(['POST'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def edit_review(request):
    """
    Sets an edit's ReviewStatus for approval or rejection,
    and sets the DateEffective.
    """
    try:
        eid = request.data['EditID']  # required
        stat = request.data['Status']  # required
        if stat != 'A' and stat != 'R':
            raise ValueError('Invalid edit status ' + str(status))
        user = request.user
        edit = Edit.objects.get(EditID=eid)
        if not user.is_superuser and not AHJUserMaintains.objects.filter(UserID=user,
                                                                         AHJPK=edit.AHJPK,
                                                                         MaintainerStatus=True).exists():
            return Response('You do not have permission to perform this action', status=status.HTTP_403_FORBIDDEN)
        edit.ReviewStatus = stat
        edit.ApprovedBy = request.user
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        if not edit.DateEffective or edit.DateEffective < tomorrow:
            edit.DateEffective = tomorrow
        edit.save()  # commit changes
        return Response('Success!', status=status.HTTP_200_OK)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


def create_row(model, obj):
    field_dict = {}
    rel_one_to_one = []
    rel_many_to_many = []
    for field, value in obj.items():
        if value == '':
            continue
        elif type(value) is dict:
            """
            NOTE: This assumes the field name matches the name of its model!
            For example, a serialized 'Contact' has the field 'Address', and Address is a model
            """
            rel_one_to_one.append(create_row(apps.get_model('ahj_app', field), value))
        elif type(value) is list:
            plurals_to_singular = {'Contacts': 'Contact'}
            if field in plurals_to_singular:
                field = plurals_to_singular[field]
            for v in value:
                rel_many_to_many.append(create_row(apps.get_model('ahj_app', field), v))
        else:
            field_dict[field] = get_enum_value_row(field, value) if field in ENUM_FIELDS else value

    model_fields = model._meta.fields

    # Establish all one-to-one relations with row
    for r in rel_one_to_one:
        found_field = False
        for field in model_fields:
            if getattr(field, 'remote_field') is not None and field.remote_field.model.__name__ == r.__class__.__name__:
                found_field = True
                field_dict[field.name] = r
        if not found_field:
            raise ValueError('Model \'{parent_model}\' has no one-to-one relation with \'{rel_model}\''.format(parent_model=model.__name__, rel_model=r.__class__.__name__))

    if model.__name__ == 'PermitIssueMethod' or model.__name__ == 'DocumentSubmissionMethod':
        row = model.objects.get(**field_dict)
    else:
        row = model.objects.create(**field_dict)

    # Establish all many-to-many relations with row
    for r in rel_many_to_many:
        rel = r.create_relation_to(row)
        setattr(rel, r.get_relation_status_field(), True)
        rel.save()

    return row

def get_serializer(row):
    serializers = {
        'AHJ': AHJSerializer,
        'AHJInspection': AHJInspectionSerializer,
        'Contact': ContactSerializer,
        'DocumentSubmissionMethod': DocumentSubmissionMethodUseSerializer,
        'AHJDocumentSubmissionMethodUse': DocumentSubmissionMethodUseSerializer,
        'EngineeringReviewRequirement': EngineeringReviewRequirementSerializer,
        'FeeStructure': FeeStructureSerializer,
        'PermitIssueMethod': PermitIssueMethodUseSerializer,
        'AHJPermitIssueMethodUse': PermitIssueMethodUseSerializer
    }
    return serializers[row.__class__.__name__]


@api_view(['POST'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def edit_addition(request):
    """
    Private front-end endpoint for passing an edit type=Addition request
    """
    try:
        source_table = request.data.get('SourceTable')
        response_data, response_status = [], status.HTTP_200_OK
        with transaction.atomic():
            model = apps.get_model('ahj_app', source_table)
            parent_table = request.data.get('ParentTable')
            parent_id = request.data.get('ParentID')
            parent_model = apps.get_model('ahj_app', parent_table)
            parent_row = parent_model.objects.get(pk=parent_id)
            ahjpk = request.data.get('AHJPK')
            ahj = AHJ.objects.get(AHJPK=ahjpk)
            new_objs = request.data.get('Value', [])

            """
            Boolean for if the addition is a one-to-many relation to AHJ.
            For example, Contact, FeeStructure and EngineeringReviewRequirement
            """
            AHJ_one_to_many = 'AHJPK' in [field.name for field in model._meta.fields]
            edits = []
            for obj in new_objs:
                if AHJ_one_to_many:
                    obj['AHJPK'] = ahj

                row = create_row(model, obj)
                edit_info_row = row.create_relation_to(parent_row)
                e = { 'User'         : request.user,
                      'AHJPK'        : ahj,
                      'SourceTable'  : edit_info_row.__class__.__name__,
                      'SourceColumn' : row.get_relation_status_field(),
                      'SourceRow'    : edit_info_row.pk,
                      'OldValue'     : None,
                      'NewValue'     : True,
                      'EditType'     : 'A' }
                edit = add_edit(e, ReviewStatus='A')
                edits.append(edit)

                response_data.append(get_serializer(row)(edit_info_row).data)
            apply_edits(ready_edits=edits)
        return Response(response_data, status=response_status)
    except Exception as e:
        print('ERROR in edit_addition', str(e))
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def edit_deletion(request):
    """
    Private front-end endpoint for passing an edit type=Deletion request
    """
    try:
        source_table = request.data.get('SourceTable')
        response_data, response_status = [], status.HTTP_200_OK
        with transaction.atomic():
            model = apps.get_model('ahj_app', source_table)
            ahjpk = request.data.get('AHJPK')
            ahj = AHJ.objects.get(AHJPK=ahjpk)
            pks_to_delete = request.data.get('Value', [])

            for pk in pks_to_delete:
                row = model.objects.get(pk=pk)
                e = { 'User'         : request.user,
                      'AHJPK'        : ahj,
                      'SourceTable'  : source_table,
                      'SourceColumn' : row.get_relation_status_field(),
                      'SourceRow'    : row.pk,
                      'OldValue'     : True,
                      'NewValue'     : False,
                      'EditType'     : 'D' }
                edit = add_edit(e)

                response_data.append(get_serializer(row)(row).data)
        return Response(response_data, status=response_status)
    except Exception as e:
        print('ERROR in edit_deletion', str(e))
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def edit_update(request):
    """
    Private front-end endpoint for passing an edit type=Addition request
    """
    try:
        response_data, response_status = [], status.HTTP_200_OK
        with transaction.atomic():
            es = request.data
            edits = []
            for e in es:
                e['AHJPK'] = AHJ.objects.get(AHJPK=e['AHJPK'])
                model = apps.get_model('ahj_app', e['SourceTable'])
                row = model.objects.get(pk=e['SourceRow'])
                old_value = getattr(row, e['SourceColumn'])

                if e['SourceColumn'] in ENUM_FIELDS and old_value is None:
                    e['OldValue'] = ''
                elif e['SourceColumn'] in ENUM_FIELDS:
                    e['OldValue'] = old_value.Value
                else:
                    e['OldValue'] = old_value

                e['User'] = request.user
                e['EditType'] = 'U'
                edit = add_edit(e, ReviewStatus='A')
                edits.append(edit)
                response_data.append(EditSerializer(edit).data)
            apply_edits(ready_edits=edits)
        return Response(response_data, status=response_status)
    except Exception as e:
        print('ERROR in edit_update', str(e))
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def edit_list(request):
    # Filtering by SourceTable, SourceRow, and SourceColumn
    source_row = request.query_params.get('AHJPK', None)
    if source_row is None:
        return Response('An AHJPK must be provided', status=status.HTTP_400_BAD_REQUEST)
    edits = Edit.objects.filter(AHJPK=source_row)
    edits = EditSerializer(edits, many=True, context={'drop_users': True}).data
    return Response(edits, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([WebpageTokenAuth])
@permission_classes([IsAuthenticated])
def user_edits(request):
    UserID = request.query_params.get('UserID', None)
    edits = Edit.objects.filter(ChangedBy=UserID)
    return Response(EditSerializer(edits, many=True).data, status=status.HTTP_200_OK)
