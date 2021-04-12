# update-edit-task.py
# The AHJ Registry
# March, 2021

from django.db import connection, transaction

def test_proc():
    with connection.cursor() as cursor:
        print('CALLING DB PROCEDURES')
        cursor.callproc('test_proc')


def edits_take_effect():
    with connection.cursor() as cursor:
        cursor.callproc('EditUpdates')
