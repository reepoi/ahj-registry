import datetime

from django.db import transaction, connection
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import EngineeringReviewRequirement, AHJPermitIssueMethodUse, \
    AHJDocumentSubmissionMethodUse, FeeStructure, AHJInspection, Contact, AHJContactRepresentative, \
    AHJInspectionContact, AHJ, Edit, DocumentSubmissionMethod, PermitIssueMethod
from .serializers import EditSerializer, ContactSerializer, \
    EngineeringReviewRequirementSerializer, PermitIssueMethodUseSerializer, DocumentSubmissionMethodUseSerializer, \
    FeeStructureSerializer, AHJInspectionSerializer


def add_contact(contact_dict : dict):
    contact = Contact()
    contact.ContactID = contact_dict.get('ContactID')
    contact.AddressID = contact_dict.get('AddressID')
    contact.FirstName = contact_dict.get('FirstName')
    contact.MiddleName = contact_dict.get('MiddleName')
    contact.LastName = contact_dict.get('LastName')
    contact.HomePhone = contact_dict.get('HomePhone')
    contact.MobilePhone = contact_dict.get('MobilePhone')
    contact.WorkPhone = contact_dict.get('WorkPhone')
    contact.ContactType = contact_dict.get('ContactType', "")
    contact.ContactTimeZone = contact_dict.get('ContactTimeZone')
    contact.Description = contact_dict.get('Description')
    contact.Email = contact_dict.get('Email')
    contact.Title = contact_dict.get('Title')
    contact.URL = contact_dict.get('URL')
    contact.PreferredContactMethod = contact_dict.get('PreferredContactMethod', "")
    contact.save()
    return contact

def add_inspection(insp_dict : dict):
    inspection = AHJInspection()
    inspection.AHJPK = AHJ.objects.get(AHJPK=int(insp_dict.get('AHJPK')))
    inspection.InspectionType = insp_dict.get('InspectionType')
    inspection.AHJInspectionName = insp_dict.get('AHJInspectionName')
    inspection.AHJInspectionNotes = insp_dict.get('AHJInspectionNotes')
    inspection.Description = insp_dict.get('Description')
    inspection.FileFolderUrl = insp_dict.get('FileFolderURL')
    inspection.TechnicianRequired = insp_dict.get('TechnicianRequired')
    inspection.InspectionStatus = insp_dict.get('InspectionStatus')
    inspection.save()
    return inspection

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
    edit.save()
    return edit

def add_feestructure(fs_dict : dict,ahjpk: int):
    fee_structure = FeeStructure()
    fee_structure.AHJPK = ahjpk
    fee_structure.FeeStructureName = fs_dict.get('FeeStructureName')
    fee_structure.FeeStructureType = fs_dict.get('FeeStructureType')
    fee_structure.Description = fs_dict.get('Description')
    fee_structure.FeeStructureStatus = fs_dict.get('FeeStructureStatus')
    fee_structure.FeeStructureID = fs_dict.get('FeeStructureID')
    fee_structure.save()
    return fee_structure

def add_engineeringreviewrequirement(eng_dict : dict, ahjpk: int):
    eng = EngineeringReviewRequirement()
    eng.AHJPK = ahjpk
    eng.Description = eng_dict.get('Description')
    eng.EngineeringReviewType = eng_dict.get('EngineeringReviewType')
    eng.RequirementLevel = eng_dict.get('RequirementLevel')
    eng.RequirementNotes = eng_dict.get('RequirementNotes')
    eng.StampType = eng_dict.get('StampType')
    eng.EngineeringReviewRequirementStatus = eng_dict.get('EngineeringReviewRequirementStatus')
    eng.save()
    return eng

####################

@api_view(['POST'])
def edit_review(request):
    try:
        eid = request.data['EditID'] # required
        stat = request.data['Status'] # requred
        if not stat is 'A' and not stat is 'R':
            raise 'Invalid edit status ' + str(status)
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

@api_view(['POST'])
def edit_addition(request):
    """
    Private front-end endpoint for passing an edit type=Addition request
    """
    try:
        source_table = request.data.get('SourceTable')
        response_data, response_status = [], status.HTTP_200_OK
        if source_table == 'Contact' :
            with connection.cursor() as cursor:
                with transaction.atomic():
                    ins_id = request.data.get('InspectionID')
                    contacts = request.data.get('Value', [])
                    # First add the contact into the db
                    for c in contacts:
                        print(ins_id)
                        contact = add_contact(c)
                        cr = None
                        if ins_id is not None: # add to inspection table
                            cr = AHJInspectionContact()
                            cr.InspectionID = AHJInspection.objects.get(InspectionID=ins_id)
                        else: # add to ahj table
                            cr = AHJContactRepresentative()
                            cr.AHJPK = AHJ.objects.get(AHJPK = int(request.data.get('AHJPK')))
                        cr.ContactID = contact
                        cr.ContactStatus = False
                        cr.save()
                        # Create the dictionary for the edit
                        e = { 'User'         : request.user,
                                 'AHJPK'        : request.data.get('AHJPK'),
                                 'InspectionID' : None if ins_id is None else AHJInspection.objects.get(InspectionID=ins_id),
                                 'SourceColumn' : 'ContactStatus',
                                 'SourceRow'    : cr.ContactID.ContactID,
                                 'OldValue'     : False,
                                 'NewValue'     : True }
                        e['SourceTable'] = 'AHJContactRepresentative' \
                            if ins_id is None else 'AHJInspectionContact'
                        edit = add_edit(e)
                        response_data.append(ContactSerializer(contact).data)
        elif source_table == 'AHJInspection':
            with connection.cursor() as cursor:
                with transaction.atomic():
                    # Add the inspection into the db
                    inspections = request.data.get('Value', [])
                    for ins in inspections:
                        ins['InspectionStatus'] = False
                        inspection = add_inspection(ins)
                        for c in ins.get('Contacts', []):
                            contact = add_contact(c)
                            cr = AHJInspectionContact()
                            cr.InspectionID = inspection
                            cr.ContactID = contact
                            cr.ContactStatus = False
                            cr.save()
                        e = { 'User'         : request.user,
                                 'AHJPK'        : request.data.get('AHJPK'),
                                 'InspectionID' : None,
                                 'SourceTable'  : 'AHJInspection',
                                 'SourceColumn' : 'InspectionStatus',
                                 'SourceRow'    : inspection.InspectionID,
                                 'OldValue'     : False,
                                 'NewValue'     : True}
                        edit = add_edit(e)
                        # TODO return inspection
                        response_data.append(AHJInspectionSerializer(inspection).data)
        elif source_table == 'FeeStructure':
            with connection.cursor() as cursor:
                with transaction.atomic():
                    fee_structures = request.data.get('Value', [])
                    for fs in fee_structures:
                        fs['FeeStructureStatus'] = False
                        fees = add_feestructure(fs,AHJ.objects.get(AHJPK=request.data.get('AHJPK')))
                        e = { 'User'         : request.user,
                                 'AHJPK'        : request.data.get('AHJPK'),
                                 'InspectionID' : request.data.get('InspectionID'), # should be NONE
                                 'SourceTable'  : 'FeeStructure',
                                 'SourceColumn' : 'FeeStructureStatus',
                                 'SourceRow'    : fees.FeeStructurePK,
                                 'OldValue'     : False,
                                 'NewValue'     : True }
                        edit = add_edit(e)
                        response_data.append(FeeStructureSerializer(fees).data)
        elif source_table == 'DocumentSubmissionMethod':
            with connection.cursor() as cursor:
                with transaction.atomic():
                    dsms = request.data.get('Value', [])
                    for dsm in dsms:
                        dsm['MethodStatus'] = False
                        au = AHJDocumentSubmissionMethodUse(AHJPK=AHJ.objects.get(AHJPK=request.data.get('AHJPK')), DocumentSubmissionMethodID=DocumentSubmissionMethod.objects.get(Value=dsm['Value']), MethodStatus=dsm['MethodStatus'])
                        au.save()
                        e = { 'User'         : request.user,
                                 'AHJPK'        : request.data.get('AHJPK'),
                                 'InspectionID' : request.data.get('InspectionID'), # should be NONE
                                 'SourceTable'  : 'DocumentSubmissionMethodUse',
                                 'SourceColumn' : 'MethodStatus',
                                 'SourceRow'    : au.UseID,
                                 'OldValue'     : False,
                                 'NewValue'     : True }
                        edit = add_edit(e)
                        response_data.append(DocumentSubmissionMethodUseSerializer(au).data)
        elif source_table == 'PermitIssueMethod':
            with connection.cursor() as cursor:
                with transaction.atomic():
                    pims = request.data.get('Value', [])
                    for pim in pims:
                        pim['MethodStatus'] = False
                        au = AHJPermitIssueMethodUse(AHJPK=AHJ.objects.get(AHJPK=request.data.get('AHJPK')), PermitIssueMethodID=PermitIssueMethod.objects.get(Value=pim['Value']),MethodStatus=pim['MethodStatus'])
                        au.save()
                        e = { 'User'         : request.user,
                                 'AHJPK'        : request.data.get('AHJPK'),
                                 'InspectionID' : request.data.get('InspectionID'), # should be NONE
                                 'SourceTable'  : 'PermitIssueMethodUse',
                                 'SourceColumn' : 'MethodStatus',
                                 'SourceRow'    : au.UseID,
                                 'OldValue'     : False,
                                 'NewValue'     : True }
                        edit = add_edit(e)
                        response_data.append(PermitIssueMethodUseSerializer(au).data)
        elif source_table == 'EngineeringReviewRequirement':
            print(request.data.get('AHJPK'))
            with connection.cursor() as cursor:
                with transaction.atomic():
                    engineeringreviewrequirements = request.data.get('Value', [])
                    for engineeringreviewrequirement in engineeringreviewrequirements:
                        engineeringreviewrequirement['EngineeringReviewRequirementStatus'] = False
                        eng = add_engineeringreviewrequirement(engineeringreviewrequirement,AHJ.objects.get(AHJPK=request.data.get('AHJPK')))
                        e = { 'User'         : request.user,
                                 'AHJPK'        : request.data.get('AHJPK'),
                                 'InspectionID' : request.data.get('InspectionID'), # should be NONE
                                 'SourceTable'  : 'EngineeringReviewRequirement',
                                 'SourceColumn' : 'EngineeringReviewRequirementStatus',
                                 'SourceRow'    : eng.EngineeringReviewRequirementID,
                                 'OldValue'     : False,
                                 'NewValue'     : True }
                        edit = add_edit(e)
                        response_data.append(EngineeringReviewRequirementSerializer(eng).data)
        else:
            print('Received unknown source table', source_table)
            raise Exception("Source table does not support edit addition")
        return Response(response_data, status=response_status)
    except Exception as e:
        print('ERROR: EDIT ADDITION', e)
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def edit_deletion(request):
    """
    Private front-end endpoint for passing an edit type=Deletion request
    """
    try:
        source_table = request.data.get('SourceTable')
        ahjpk = request.data['AHJPK']
        response_data, response_status = [], status.HTTP_200_OK
        if source_table == 'Contact' :
            with transaction.atomic():
                insp_id = request.data.get('InspectionID')
                cids = request.data.get('Value', [])
                for cid in cids:
                    cr = AHJContactRepresentative.objects.get(AHJPK=ahjpk, ContactID=cid) \
                        if insp_id is None else \
                        AHJInspectionContact.objects.get(InspectionID=insp_id, ContactID=cid)
                    # Create the dictionary for the edit
                    e = { 'User'       : request.user,
                        'AHJPK'        : ahjpk,
                        'InspectionID' : None if request.data.get('InspectionID') is None else AHJInspection.objects.get(InspectionID=request.data.get('InspectionID')),
                        'SourceColumn' : 'ContactStatus',
                        'SourceRow'    : cid,
                        'OldValue'     : True,
                        'NewValue'     : False }
                    e['SourceTable'] = 'AHJContactRepresentative' \
                        if insp_id is None else 'AHJInspectionContact'
                    print(e['OldValue'])
                    edit = add_edit(e)
                    cont = Contact.objects.get(ContactID=cid)
                    response_data.append(ContactSerializer(cont).data)
        elif source_table == 'AHJInspection':
            with transaction.atomic():
                # Add the inspection into the db
                iids = request.data.get('Value', [])
                print(iids)
                for iid in iids:
                    if iid is None:
                        continue
                    inspection = AHJInspection.objects.get(AHJPK=ahjpk, InspectionID=iid)
                    e = { 'User'       : request.user,
                        'AHJPK'        : ahjpk,
                        'InspectionID' : AHJInspection.objects.get(InspectionID=iid),
                        'SourceTable'  : 'AHJInspection',
                        'SourceColumn' : 'InspectionStatus',
                        'SourceRow'    : inspection.InspectionID,
                        'OldValue'     : True,
                        'NewValue'     : False }
                    edit = add_edit(e)
                    response_data.append(EditSerializer(edit).data)
        elif source_table == 'FeeStructure':
            with transaction.atomic():
                fspks = request.data.get('Value', [])
                for fspk in fspks:
                    fees = FeeStructure.objects.get(AHJPK=ahjpk, FeeStructurePK=fspk)
                    e = { 'User'       : request.user,
                        'AHJPK'        : ahjpk,
                        'InspectionID' : request.data.get('InspectionID'),
                        'SourceTable'  : 'FeeStructure',
                        'SourceColumn' : 'FeeStructureStatus',
                        'SourceRow'    : fees.FeeStructurePK,
                        'OldValue'     : True,
                        'NewValue'     : False }
                    edit = add_edit(e)
                    response_data.append(EditSerializer(edit).data)
        elif source_table == 'DocumentSubmissionMethod':
            with transaction.atomic():
                dsmpks = request.data.get('Value', [])
                for dsmpk in dsmpks:
                    dsmpk = AHJDocumentSubmissionMethodUse.objects.get(AHJPK=ahjpk, UseID=dsmpk)
                    e = { 'User'       : request.user,
                        'AHJPK'        : ahjpk,
                        'InspectionID' : request.data.get('InspectionID'),
                        'SourceTable'  : 'DocumentSubmissionMethodUse',
                        'SourceColumn' : 'MethodStatus',
                        'SourceRow'    : dsmpk.UseID,
                        'OldValue'     : True,
                        'NewValue'     : False }
                    edit = add_edit(e)
                    response_data.append(EditSerializer(edit).data)
        elif source_table == 'PermitIssueMethod':
            with transaction.atomic():
                pimpks = request.data.get('Value', [])
                for pimpk in pimpks:
                    pim = AHJPermitIssueMethodUse.objects.get(AHJPK=ahjpk, UseID=pimpk)
                    e = { 'User'       : request.user,
                        'AHJPK'        : ahjpk,
                        'InspectionID' : request.data.get('InspectionID'),
                        'SourceTable'  : 'PermitIssueMethodUse',
                        'SourceColumn' : 'MethodStatus',
                        'SourceRow'    : pim.UseID,
                        'OldValue'     : True,
                        'NewValue'     : False }
                    edit = add_edit(e)
                    response_data.append(EditSerializer(edit).data)
        elif source_table == 'EngineeringReviewRequirement':
            with transaction.atomic():
                engpks = request.data.get('Value', [])
                for engpk in engpks:
                    eng = EngineeringReviewRequirement.objects.get(AHJPK=ahjpk, EngineeringReviewRequirementID=engpk)
                    e = { 'User'       : request.user,
                        'AHJPK'        : ahjpk,
                        'InspectionID' : request.data.get('InspectionID'),
                        'SourceTable'  : 'EngineeringReviewRequirement',
                        'SourceColumn' : 'EngineeringReviewRequirementStatus',
                        'SourceRow'    : eng.EngineeringReviewRequirementID,
                        'OldValue'     : True,
                        'NewValue'     : False }
                    edit = add_edit(e)
                    response_data.append(EditSerializer(edit).data)
        else:
            print('Received unknown source table', source_table)
            raise Exception("Source table does not support edit addition")
        return Response(response_data, status=response_status)
    except Exception as e:
        print('ERROR in edit_deletion', str(e))
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def edit_update(request):
    """
    Private front-end endpoint for passing an edit type=Addition request
    """
    try:
        # TODO we need to santiize the given fields a little
        response_data, response_status = [], status.HTTP_200_OK
        with transaction.atomic():
            es = request.data
            print(es)
            for e in es:
                e['User'] = request.user
                e['InspectionID'] = None if e['InspectionID'] is None else AHJInspection.objects.get(InspectionID=e['InspectionID'])
                edit = add_edit(e)
                response_data.append(EditSerializer(edit).data)
        return Response(response_data, status=response_status)
    except Exception as e:
        print('ERROR: EDIT UPDATE', e)
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
    # source_table = request.query_params.get('SourceTable', None)
    # print(request.query_params)
    # if source_table is not None:
    #     edits = edits.filter(SourceTable=source_table)
    source_row = request.query_params.get('AHJPK', None)
    # print(source_row, type(source_row))
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
