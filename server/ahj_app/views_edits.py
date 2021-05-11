import datetime

from django.apps import apps
from django.db import transaction, connection
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import EngineeringReviewRequirement, AHJPermitIssueMethodUse, \
    AHJDocumentSubmissionMethodUse, FeeStructure, AHJInspection, Contact, AHJContactRepresentative, \
    AHJInspectionContact, AHJ, Edit, DocumentSubmissionMethod, PermitIssueMethod
from .serializers import AHJSerializer, EditSerializer, ContactSerializer, \
    EngineeringReviewRequirementSerializer, PermitIssueMethodUseSerializer, DocumentSubmissionMethodUseSerializer, \
    FeeStructureSerializer, AHJInspectionSerializer


def add_edit(edit_dict : dict):
    edit = Edit()
    edit.ChangedBy = edit_dict.get('User')
    edit.DateRequested = datetime.date.today()
    edit.AHJPK = edit_dict.get('AHJPK')
    edit.InspectionID = edit_dict.get('InspectionID')
    edit.SourceTable = edit_dict.get('SourceTable')
    edit.SourceColumn = edit_dict.get('SourceColumn')
    edit.SourceRow = edit_dict.get('SourceRow')
    edit.OldValue = edit_dict.get('OldValue')
    edit.NewValue = edit_dict.get('NewValue')
    edit.ReviewStatus = 'P'
    edit.EditType = edit_dict.get('EditType')
    edit.save()
    return edit


def apply_edits():
    ready_edits = Edit.objects.filter(
        ReviewStatus='A',
        DateEffective=datetime.date.today()
    ).exclude(ApprovedBy=None)
    for edit in ready_edits:
        model = apps.get_model('ahj_app', edit.SourceTable)
        parent_rel = 'AHJPK' if edit.InspectionID is None else 'InspectionID'
        search_fields = {
            model._meta.pk.name: edit.SourceRow
        }
        if len(model._meta.unique_together) > 0:
            search_fields[parent_rel] = getattr(edit, parent_rel)
        row = model.objects.filter(**search_fields)
        row.update(**{
            edit.SourceColumn: edit.NewValue
        })

####################

@api_view(['POST'])
def edit_review(request):
    try:
        eid = request.data['EditID'] # required
        stat = request.data['Status'] # requred
        if stat != 'A' and stat != 'R':
            raise ValueError('Invalid edit status ' + str(status))
        with transaction.atomic():
            edit = Edit.objects.get(EditID=int(eid))
            edit.ReviewStatus = stat
            edit.ApprovedBy = request.user
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            if not edit.DateEffective or edit.DateEffective < tomorrow:
                edit.DateEffective = tomorrow
            edit.save() # commit changes
            print(eid)
        return Response('Success!', status=status.HTTP_200_OK)
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


def create_row(model, obj):  # TODO: Adding DocumentSub/PermitIssue creates a new row
    field_dict = {}
    child_rows = []
    for field, value in obj.items():
        if type(value) is dict:
            """
            NOTE: This assumes the field name matches the name of its model!
            For example, a 'Contact' has the field 'Address', and Address is a model
            """
            child_rows.append(create_row(apps.get_model('ahj_app', field), value))
        else:
            field_dict[field] = value
    model_fields = model._meta.fields
    for child in child_rows:
        found_child_relation = False
        for field in model_fields:
            if getattr(field, 'remote_field') is not None and field.remote_field.model.__name__ == child.__class__.__name__:
                found_child_relation = True
                field_dict[field.name] = child
        if not found_child_relation:
            raise ValueError('Model \'{parent_model}\' has no field related to \'{child_model}\''.format(parent_model=model.__name__, child_model=child.__class__.__name__))
    print(field_dict)
    # Could possibly generalize this check to being 'is table for enum values'
    if model.__name__ == 'PermitIssueMethod' or model.__name__ == 'DocumentSubmissionMethod':
        return model.objects.get(**field_dict)
    return model.objects.create(**field_dict)

def get_serializer(row):
    serializers = {
        'AHJ': AHJSerializer,
        'AHJInspection': AHJInspectionSerializer,
        'Contact': ContactSerializer,
        'DocumentSubmissionMethod': DocumentSubmissionMethodUseSerializer,
        'EngineeringReviewRequirement': EngineeringReviewRequirementSerializer,
        'FeeStructure': FeeStructureSerializer,
        'PermitIssueMethod': PermitIssueMethodUseSerializer
    }
    return serializers[row.__class__.__name__]


@api_view(['POST'])
def edit_addition(request):  # TODO: prevent adding Address/Location directly? It shouldn't happen
    """
    Private front-end endpoint for passing an edit type=Addition request
    """
    try:
        source_table = request.data.get('SourceTable')
        response_data, response_status = [], status.HTTP_200_OK
        with connection.cursor() as cursor:
            with transaction.atomic():
                model = apps.get_model('ahj_app', source_table)
                new_objs = request.data.get('Value', [])
                for obj in new_objs:
                    ahjpk = request.data.get('AHJPK')
                    ahj = None if ahjpk is None else AHJ.objects.get(AHJPK=ahjpk)
                    inspectionid = request.data.get('InspectionID')
                    inspection = None if inspectionid is None else AHJInspection.objects.get(InspectionID=inspectionid)

                    if 'AHJPK' in obj:
                        """
                        The addition is a one-to-many relation to AHJ.
                        For example, FeeStructure and EngineeringReviewRequirement
                        """
                        obj['AHJPK'] = ahj

                    row = create_row(model, obj)
                    parent_row = ahj if inspection is None else inspection
                    edit_info_row = row.create_relation_to(parent_row)
                    e = { 'User'         : request.user,
                          'AHJPK'        : ahj,
                          'InspectionID' : inspection,
                          'SourceTable'  : edit_info_row.__class__.__name__,
                          'SourceColumn' : row.get_relation_status_field(),
                          'SourceRow'    : edit_info_row.pk,
                          'OldValue'     : False,
                          'NewValue'     : None,
                          'EditType'     : 'A' }
                    edit = add_edit(e)

                    # For Contact, Contact should be returned, not its many-to-many relation table row
                    to_serialize = row if source_table == 'Contact' else edit_info_row
                    response_data.append(get_serializer(row)(to_serialize).data)
        return Response(response_data, status=response_status)
    except Exception as e:
        print('ERROR in edit_addition', e)
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def edit_deletion(request):  # TODO: Make this called for rejecting additions to set their Status field to false
    """
    Private front-end endpoint for passing an edit type=Deletion request
    """
    try:
        source_table = request.data.get('SourceTable')
        response_data, response_status = [], status.HTTP_200_OK
        with connection.cursor() as cursor:
            with transaction.atomic():
                model = apps.get_model('ahj_app', source_table)
                new_objs = request.data.get('Value', [])
                for obj in new_objs:
                    ahjpk = request.data.get('AHJPK')
                    ahj = None if ahjpk is None else AHJ.objects.get(AHJPK=ahjpk)
                    inspectionid = request.data.get('InspectionID')
                    inspection = None if inspectionid is None else AHJInspection.objects.get(InspectionID=inspectionid)
                    parent_row = ahj if inspection is None else inspection
                    row = model.objects.get(pk=obj)
                    edit_info_row = row.get_relation_to(parent_row)
                    e = { 'User'         : request.user,
                          'AHJPK'        : ahj,
                          'InspectionID' : inspection,
                          'SourceTable'  : edit_info_row.__class__.__name__,
                          'SourceColumn' : row.get_relation_status_field(),
                          'SourceRow'    : edit_info_row.pk,
                          'OldValue'     : getattr(edit_info_row, row.get_relation_status_field()),  # None or True
                          'NewValue'     : False,
                          'EditType'     : 'D' }
                    edit = add_edit(e)

                    if source_table == 'Contact':
                        response_data.append(ContactSerializer(row).data)  # TODO: Why need contact?
                    else:
                        response_data.append(EditSerializer(edit).data)
        return Response(response_data, status=response_status)
    except Exception as e:
        print('error in edit_deletion', str(e))
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def edit_update(request):
    """
    Private front-end endpoint for passing an edit type=Addition request
    """
    try:
        response_data, response_status = [], status.HTTP_200_OK
        with transaction.atomic():
            es = request.data
            for e in es:
                e['AHJPK'] = AHJ.objects.get(AHJPK=e['AHJPK'])
                model = apps.get_model('ahj_app', e['SourceTable'])
                row = model.objects.get(pk=e['SourceRow'])
                e['OldValue'] = getattr(row, e['SourceColumn'])
                e['User'] = request.user
                e['InspectionID'] = None if e['InspectionID'] is None else AHJInspection.objects.get(InspectionID=e['InspectionID'])
                e['EditType'] = 'U'
                edit = add_edit(e)
                response_data.append(EditSerializer(edit).data)
        return Response(response_data, status=response_status)
    except Exception as e:
        print('ERROR in edit_update', e)
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def edit_submit(request):
    # if check_is_authenticated(request):
    #     return get_not_authenticated_response()
    serializer = EditSerializer(data=request.data, context={'user': request.user})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    edit = serializer.create()
    edit.save()
    return Response(EditSerializer(edit).data, status=status.HTTP_200_OK)

@api_view(['GET'])
def edit_list(request):
    edits = Edit.objects.all()
    # Filtering by SourceTable, SourceRow, and SourceColumn
    source_row = request.query_params.get('AHJPK', None)
    if source_row is not None:
        edits = edits.filter(AHJPK=source_row)
    edits = EditSerializer(edits, many=True).data
    return Response(edits, status=status.HTTP_200_OK)

@api_view(['GET'])
def user_edits(request):
    UserID = request.query_params.get('UserID', None)
    edits = Edit.objects.filter(ChangedBy=UserID)
    return Response(EditSerializer(edits, many=True).data, status=status.HTTP_200_OK)

@api_view(['GET'])
def unconfirmed_conts(request):
    source_row = request.query_params.get('SourceRow')
    conts = AHJContactRepresentative.objects.filter(AHJPK=int(source_row), ContactStatus=0)
    return ContactSerializer(conts, many=True).data

@api_view(['GET'])
def unconfirmed_insps(request):
    source_row = request.query_params.get('SourceRow')
    insps = AHJInspection.objects.filter(AHJPK=int(source_row), InspectionStatus=0)
    return AHJInspectionSerializer(insps, many=True).data

@api_view(['GET'])
def unconfirmed_err(request):
    return
