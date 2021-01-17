from .models import *
from simple_history.models import HistoricalRecords
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from .serializers import *
from rest_framework.parsers import JSONParser
from django.apps import apps
import json
import csv
from ahj_gis.constants import GOOGLE_GEOCODING_API_KEY
from googlemaps import Client

gmaps = Client(key=GOOGLE_GEOCODING_API_KEY)


def get_location(request):
    """
    Returns the latlng of an address given in the request Address parameter
    The format is an Orange Button Location object: https://obeditor.sunspec.org/#/?views=Location
    """
    location = {
            'Latitude': {
                'Value': None
            },
            'Longitude': {
                'Value': None
            }
    }
    address = request.GET.get('Address', None)
    if address is not None:
        geo_res = gmaps.geocode(address)
        if len(geo_res) != 0:
            latitude = geo_res[0]['geometry']['location']['lat']
            longitude = geo_res[0]['geometry']['location']['lng']
            location['Latitude']['Value'] = latitude
            location['Longitude']['Value'] = longitude
    return location


def get_ahj_diff(ahj):
    new_record = ahj.history.first()
    old_record = ahj.history.first()
    if new_record is None:
        new_record = old_record
    delta = new_record.diff_against(old_record)
    for change in delta.changes:
        print("{} changed from {} to {}".format(change.field, change.old, change.new))


def export_ahjs_csv():
    with open('ahjs_all.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['AHJID', 'AHJName', 'StateProvince'])
        ahjs = AHJ.objects.all()
        count = 1
        for ahj in ahjs:
            writer.writerow([ahj.AHJID, ahj.AHJName, Address.objects.get(AHJ=ahj).StateProvince])
            print('Written AHJ %i' % count)
            count += 1


def export_ahjs_no_polygon_csv():
    with open('ahjs_no_polygon.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['AHJID', 'AHJName', 'StateProvince'])
        ahjs = AHJ.objects.filter(county_mpoly=None).filter(city_mpoly=None)
        count = 1
        for ahj in ahjs:
            writer.writerow([ahj.AHJID, ahj.AHJName, Address.objects.get(AHJ=ahj).StateProvince])
            print('Written AHJ %i' % count)
            count += 1


def export_ahjs_both_polygons_csv():
    with open('ahjs_no_polygon.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['AHJID', 'AHJName', 'StateProvince'])
        ahjs = AHJ.objects.exclude(county_mpoly=None).exclude(city_mpoly=None)
        count = 1
        for ahj in ahjs:
            writer.writerow([ahj.AHJID, ahj.AHJName, Address.objects.get(AHJ=ahj).StateProvince])
            print('Written AHJ %i' % count)
            count += 1


def export_polygons_csv():
    with open('polygons_all.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['NAMELSAD', 'STATEABBR', 'STATEFP'])
        counties = County.objects.all()
        cities = City.objects.all()
        count = 1
        for c in counties:
            writer.writerow([c.NAMELSAD, c.STATEABBR, c.STATEFP])
            print('Written County %i' % count)
            count += 1
        for c in cities:
            writer.writerow([c.NAMELSAD, c.STATEABBR, c.STATEFP])
            print('Written City %i' % count)
            count += 1


def export_polygons_no_ahj_csv():
    with open('polygons_no_ahj.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['NAMELSAD', 'STATEABBR', 'STATEFP'])
        counties = County.objects.filter(ahj=None)
        cities = City.objects.filter(ahj=None)
        count = 1
        for c in counties:
            writer.writerow([c.NAMELSAD, c.STATEABBR, c.STATEFP])
            print('Written County %i' % count)
            count += 1
        for c in cities:
            writer.writerow([c.NAMELSAD, c.STATEABBR, c.STATEFP])
            print('Written City %i' % count)
            count += 1


def export_county_polygon_geoid_csv():
    with open('county_polygon_geoid.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['NAMELSAD', 'STATEABBR', 'GEOID'])
        counties = County.objects.all()
        count = 1
        for c in counties:
            writer.writerow([c.NAMELSAD, c.STATEABBR, c.GEOID])
            print('Written County %i' % count)
            count += 1


def export_city_polygon_geoid_csv():
    with open('city_polygon_geoid.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['NAMELSAD', 'STATEABBR', 'GEOID'])
        cities = City.objects.all()
        count = 1
        for c in cities:
            writer.writerow([c.NAMELSAD, c.STATEABBR, c.GEOID])
            print('Written City %i' % count)
            count += 1

def export_ahj_polygon_geoid_csv():
    with open('ahj_polygon_geoid.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Census_match_name', 'GEOID'])
        ahjs = AHJ.objects.all()
        count = 1
        for ahj in ahjs:
            if ahj.mpoly:
                writer.writerow([ahj.mpoly.STATEABBR + ': ' + ahj.mpoly.NAMELSAD, ahj.mpoly.GEOID])
                print('Written AHJ %i' % count)
            else:
                print('skip')
            count += 1


def export_dupe_ahjs_csv():
    with open('dupe_ahjs.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['AHJName', 'STATEABBR'])
        addrs = Address.objects.all().order_by('StateProvince')
        current_state = addrs.first().StateProvince
        temp_addrs = addrs.filter(StateProvince=current_state).order_by('AHJ__AHJName')
        i = 0
        dupe_count = 0
        prev = temp_addrs.first().AHJ.AHJName
        curr = ''
        print('starting loop')
        for x in range(len(addrs)):
            temp_state = addrs[x].StateProvince
            if current_state != temp_state:
                current_state = temp_state
                temp_addrs = addrs.filter(StateProvince=current_state).order_by('AHJ__AHJName')
                print('Filtering State')
                i = 0
            curr = temp_addrs[i].AHJ.AHJName
            if i != 0 and curr == prev:
                dupe_count += 1
                writer.writerow([temp_addrs[i].AHJ.AHJName, temp_addrs[i].StateProvince])
                print('DUPE: %s, %s' % (temp_addrs[i].AHJ.AHJName, temp_addrs[i].StateProvince))
            prev = curr
            print(i)
            i += 1


def set_view_mode(request, hide_ui_fields, called_by_view):
    confirmed = False
    highest_voted = False
    view_mode = request.GET.get('view', '')
    if view_mode == 'confirmed':
        confirmed = True
    elif view_mode == 'highest_voted':
        highest_voted = True
    return {'confirmed_edits_only': confirmed, 'highest_vote_rating': highest_voted, 'hide_ui_fields': hide_ui_fields, 'called_by_view': called_by_view}


def create_edit(request):
    if type(request.data) is list:
        return create_edit_mass(request)
    edit_creation_message_status = process_edit_creation(request.data, request.user)
    return Response(edit_creation_message_status[0], status=edit_creation_message_status[1])


def create_edit_mass(request):
    edit_creation_message_statuses = []
    edit_data_array = request.data
    for edit_data in edit_data_array:
        edit_creation_message_statuses.append(process_edit_creation(edit_data, request.user))
    created_edits = []
    errors = {}
    for x in range(len(edit_creation_message_statuses)):
        if edit_creation_message_statuses[x][1] == status.HTTP_201_CREATED:
            created_edits.append(edit_creation_message_statuses[x][0])
        else:
            errors[x] = edit_creation_message_statuses[x][0]
    if errors:
        response_status = status.HTTP_400_BAD_REQUEST
    else:
        response_status = status.HTTP_200_OK
    return Response({'created': EditSerializer(created_edits, many=True).data, 'errors': errors}, status=response_status)


def process_edit_creation(edit_data, user):
    edit_serializer = EditSerializer(data=edit_data)
    if edit_serializer.is_valid():
        edit = Edit(**edit_serializer.validated_data)

        if not edit.validate_RecordType():
            return {'detail': 'Invalid record type'}, status.HTTP_400_BAD_REQUEST

        edit.ModifyingUserID = user.id

        if edit.EditType == 'create':
            if edit.RecordType != 'AHJ':
                if edit.ParentID == '' or not edit.validate_ParentRecordType():
                    return {'detail': 'Invalid parent record type'}, status.HTTP_400_BAD_REQUEST
            edit.create_record()
        elif edit.EditType == 'update':
            if edit.RecordID == '':
                return {'detail': 'No record ID was given'}, status.HTTP_400_BAD_REQUEST
            if edit.get_record() is None:
                return {'detail': 'Record not found'}, status.HTTP_404_NOT_FOUND
            if not edit.validate_FieldName():
                return {'detail': 'Invalid field name.'}, status.HTTP_400_BAD_REQUEST
            if not edit.clean_Value():
                return {'detail': 'Invalid value given.'}, status.HTTP_400_BAD_REQUEST
            if Edit.objects.filter(RecordID=edit.RecordID).filter(FieldName=edit.FieldName).filter(IsConfirmed=None).filter(Value=edit.Value).exists():
                return {'detail': 'An unconfirmed edit with this value already exists.'}, status.HTTP_400_BAD_REQUEST
            edit.PreviousValue = getattr(edit.get_record(), edit.FieldName)
            if edit.Value == edit.PreviousValue:
                return {'detail': 'This edit has the same value as the record'}, status.HTTP_400_BAD_REQUEST
        elif edit.EditType == 'delete':
            if edit.get_record() is None:
                return {'detail': 'Record not found'}, status.HTTP_404_NOT_FOUND
            if not check_record_edit_create_confirmed(edit.get_record()):
                return {'detail': 'Cannot make delete request records awaiting confirmation'}, status.HTTP_403_FORBIDDEN
        else:
            return {'detail': 'Invalid edit type'}, status.HTTP_400_BAD_REQUEST
        if user.is_superuser or edit.is_record_owner(user.id):
            edit.accept(user.id)
        else:
            edit.save()
            record_owners = edit.get_record_owners()
            for owner in record_owners:
                send_edit_confirmation_email(owner, edit)
        return EditSerializer(edit).data, status.HTTP_201_CREATED
    return edit_serializer.errors, status.HTTP_400_BAD_REQUEST


def set_edit(request, pk):
    edit = Edit.objects.filter(pk=pk).first()
    if edit is None:
        return Response({'detail': 'Edit not found'}, status=status.HTTP_404_NOT_FOUND)
    user = request.user
    confirm_status = request.GET.get('confirm', '')
    if confirm_status != '':
        return set_edit_status(confirm_status, user, edit)
    vote_status = request.GET.get('vote', '')
    if vote_status != '':
        return set_edit_vote(vote_status, user, edit)
    return Response(EditSerializer(edit).data, status=status.HTTP_200_OK)


def set_edit_status(confirm_status, user, edit):
    if edit.IsConfirmed is not None:
        return Response({'detail': 'Edit has already been processed. Please submit another edit.'}, status=status.HTTP_403_FORBIDDEN)
    if user.is_superuser or edit.is_record_owner(user.id):
        if confirm_status == 'accepted':
            edit.accept(user_id=user.id)
        elif confirm_status == 'rejected':
            edit.reject(user_id=user.id)
        return Response(EditSerializer(edit).data)
    else:
        return Response({'detail': 'Unauthorized to process edit.'}, status=status.HTTP_401_UNAUTHORIZED)


def set_edit_vote(vote_status, user, edit):
    if edit.IsConfirmed or user.id == edit.ModifyingUserID:
        return Response(EditSerializer(edit).data, status=status.HTTP_200_OK)
    if vote_status == 'upvote':
        rating = True
    elif vote_status == 'downvote':
        rating = False
    elif vote_status == 'none':
        rating = None
    else:
        return Response(EditSerializer(edit).data, status=status.HTTP_200_OK)
    vote = Vote.objects.filter(Edit=edit).filter(VotingUserID=user.id).first()
    if vote is None:
        if rating is not None:
            Vote.objects.create(Edit=edit, VotingUserID=user.id, Rating=rating)
    else:
        if rating is None:
            vote.delete()
        elif vote.Rating != rating:
            vote.Rating = rating
            vote.save()
    edit.set_vote_rating()
    return Response(EditSerializer(edit).data, status=status.HTTP_200_OK)
