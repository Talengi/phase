
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from annoying.functions import get_object_or_None

from transmittals.validation import Validator, AndValidator, CSVLineValidator
from accounts.models import User


class MissingLeaderValidator(Validator):
    """Checks that the required leader is set."""
    error = 'The leader is missing'
    error_key = 'missing_leader'

    def test(self, import_line):
        if import_line.csv_data['review_start_date']:
            return bool(import_line.csv_data['review_leader'])
        else:
            return True


class UnknownLeaderValidator(Validator):
    """Checks that the leader's account exists."""
    error = 'The leader is unknown'
    error_key = 'unknown_leader'

    def test(self, import_line):
        if not import_line.csv_data['review_start_date']:
            return True

        leader_name = import_line.csv_data['review_leader']
        category = import_line.trs_import.doc_category
        qs = User.objects.filter(categories=category)
        user = get_object_or_None(qs, name=leader_name)
        return bool(user)


class LeaderValidator(AndValidator):
    """Checks that the leader is set and exists."""
    error_key = 'leader'
    VALIDATORS = (
        MissingLeaderValidator(),
        UnknownLeaderValidator()
    )


class ApproverValidator(Validator):
    """Checks that the approver's account exists."""
    error = 'The approver is unknown'
    error_key = 'unknown_approver'

    def test(self, import_line):
        if not import_line.csv_data['review_approver']:
            return True

        approver_name = import_line.csv_data['review_approver']
        category = import_line.trs_import.doc_category
        qs = User.objects.filter(categories=category)
        user = get_object_or_None(qs, name=approver_name)
        return bool(user)


class MyCSVLineValidator(CSVLineValidator):
    def get_validators(self):
        validators = super(MyCSVLineValidator, self).get_validators() + (
            LeaderValidator(),
            ApproverValidator(),
        )
        return validators