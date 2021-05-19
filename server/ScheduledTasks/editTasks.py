# update-edit-task.py
# The AHJ Registry
# March, 2021
from django.conf import settings
import sys
sys.path.append('..')
from ahj_app.views_edits import apply_edits

def test_proc():
    if settings.APPLY_APPROVED_EDITS:
        apply_edits()


def edits_take_effect():
    if settings.APPLY_APPROVED_EDITS:
        apply_edits()
