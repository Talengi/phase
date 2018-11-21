# -*- coding: utf-8 -*-


import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible


@deconstructible
class StringNumberValidator(object):
    """Validate numbers that should be typed in with a fixed length"""

    base_regex = r'\d{%d}'
    message = _('The value is incorrect')
    code = 'invalid'

    def __init__(self, length=4):
        self.length = length
        self.regex = re.compile(self.base_regex % length)

    def __call__(self, value):
        if not self.regex.match(value):
            raise ValidationError(self.message, self.code)

    def __eq__(self, validator):
        return self.length == validator.length
