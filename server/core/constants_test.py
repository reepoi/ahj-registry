AHJ_LIST_ENDPOINT = lambda view: '/api/v1/ahj/?view=%(view)s' % {'view': view}
AHJ_DETAIL_ENDPOINT = lambda AHJID, view: '/api/v1/ahj/%(AHJID)s/?view=%(view)s' % {'AHJID': AHJID, 'view': view}

AHJ_OWNER_ENDPOINT = lambda mode, user_id, AHJID: '/api/v1/ahj/ownership/?mode=%(mode)s&user=%(user_id)i&AHJID=%(AHJID)s' % {'mode': mode, 'user_id': user_id, 'AHJID': AHJID}

EDIT_SUBMIT_ENDPOINT = '/api/v1/edit/submit/'
EDIT_DETAIL_ENDPOINT_CONFIRM = lambda pk, status: '/api/v1/edit/%i/?confirm=%s' % (pk, status)
EDIT_DETAIL_ENDPOINT_VOTE = lambda pk, rating: '/api/v1/edit/%i/?vote=%s' % (pk, rating)

EDIT_CREATE_AHJ = {'RecordType': 'AHJ', 'EditType': 'create'}
EDIT_CREATE_ADDRESS = lambda ParentID, ParentRecordType: {'RecordType': 'Address', 'ParentID': ParentID, 'ParentRecordType': ParentRecordType, 'EditType': 'create'}
EDIT_CREATE_CONTACT = lambda ParentID, ParentRecordType: {'RecordType': 'Contact', 'ParentID': ParentID, 'ParentRecordType': ParentRecordType, 'EditType': 'create'}
EDIT_CREATE_ENG_REV_REQ = lambda ParentID: {'RecordType': 'EngineeringReviewRequirement', 'ParentID': ParentID, 'ParentRecordType': 'AHJ', 'EditType': 'create'}
EDIT_CREATE_LOCATION = lambda ParentID: {'RecordType': 'Location', 'ParentID': ParentID, 'ParentRecordType': 'Address', 'EditType': 'create'}
EDIT_CREATE_AHJ_INSPECTION = lambda ParentID: {'RecordType': 'AHJInspection', 'ParentID': ParentID, 'ParentRecordType': 'AHJ', 'EditType': 'create'}
EDIT_CREATE_FEE_STRUCTURE = lambda ParentID: {'RecordType': 'FeeStructure', 'ParentID': ParentID, 'ParentRecordType': 'AHJ', 'EditType': 'create'}
EDIT_CREATE_DOCUMENT_SUBMISSION_METHOD = lambda ParentID: {'RecordType': 'DocumentSubmissionMethod', 'ParentID': ParentID, 'ParentRecordType': 'AHJ', 'EditType': 'create'}
EDIT_CREATE_PERMIT_ISSUE_METHOD = lambda ParentID: {'RecordType': 'PermitIssueMethod', 'ParentID': ParentID, 'ParentRecordType': 'AHJ', 'EditType': 'create'}

EDIT_DELETE = lambda RecordID, RecordType: {'RecordID': RecordID, 'RecordType': RecordType, 'EditType': 'delete'}

EDIT_UPDATE = lambda RecordID, RecordType, FieldName, Value: {'RecordID': RecordID, 'RecordType': RecordType, 'EditType': 'update', 'FieldName': FieldName, 'Value': Value}
