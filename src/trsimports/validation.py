# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re


class Validator(object):
    """An object which purpose is to check a single validation point."""
    error = 'Undefined error'

    def test(self, trs_import):
        raise NotImplementedError()

    def validate(self, trs_import):
        """Performs the validation.

        The `validate` method must return None if the validation passed, or
        a string containing the error message if any.

        """
        if self.test(trs_import):
            return None
        else:
            return self.error


class CompositeValidator(Validator):
    def __init__(self, validators):
        self.validators = validators

    def validate(self, trs_import):
        errors = dict()
        for name, validator in self.validators.items():
            error = validator.validate(trs_import)
            if error:
                errors[name] = error

        return errors


class DirnameValidator(Validator):
    error = 'The directory name is incorrect'
    pattern = 'FAC(09001|10005)-\w{3}-\w{3}-TRS-\d{5}'

    def test(self, trs_import):
        return re.match(self.pattern, trs_import.basename)


class TrsValidator(CompositeValidator):
    def __init__(self):
        super(TrsValidator, self).__init__({
            'invalid_dirname': DirnameValidator(),
        })
