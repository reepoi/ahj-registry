# update-edit-task.py
# The AHJ Registry
# March, 2021
from django.conf import settings
import sys
sys.path.append('..')
from ahj_app import views_edits, views_ahjsearch_api


def test_proc():
    # if settings.APPLY_APPROVED_EDITS:
    #     views_edits.apply_edits()
    views_ahjsearch_api.deactivate_expired_api_tokens()


def edits_take_effect():
    if settings.APPLY_APPROVED_EDITS:
        views_edits.apply_edits()


def deactivate_expired_api_tokens():
    views_ahjsearch_api.deactivate_expired_api_tokens()
