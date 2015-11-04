# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class TransmittalError(Exception):
    pass


class MissingRevisionsError(TransmittalError):
    pass


class InvalidRevisionsError(TransmittalError):
    pass


class InvalidCategoryError(TransmittalError):
    pass
