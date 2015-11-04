# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from transmittals import errors
from transmittals.models import OutgoingTransmittalRevision, TransmittableMixin
from transmittals.forms import (
    OutgoingTransmittalForm, OutgoingTransmittalRevisionForm)


class FieldWrapper(object):
    """Utility class to access fields scattered across multiple objects.

    >>> o1 = {'var1': 'toto', 'var2': 'tata'}
    >>> o2 = {'var3': 'riri', 'var4': 'fifi'}
    >>> wrapped = FieldWrapper((o1, o2))
    >>> wrapped.var1
    'toto'
    >>> wrapped.var3
    'riri
    >>> wrapped['var4']
    'fifi'

    """

    def __init__(self, objects):
        self.objects = objects

    def __getitem__(self, attr):
        it = iter(self.objects)

        try:
            obj = it.next()
            while not hasattr(obj, attr):
                obj = it.next()
            return getattr(obj, attr)
        except StopIteration:
            raise AttributeError('Attribute {} not found'.format(attr))

    def __getattr__(self, attr):
        return self[attr]


def create_transmittal(from_category, to_category, revisions):
    """Create an outgoing transmittal with the given revisions."""

    # Do we have a list of revisions?
    if not isinstance(revisions, list) or len(revisions) == 0:
        raise errors.MissingRevisionsError(
            'Please provide a valid list of transmittals')

    # The "from" category must contain transmittable documents
    from_type = from_category.revision_class()
    if not issubclass(from_type, TransmittableMixin):
        raise errors.InvalidCategoryError(
            'Source category must contain transmittable documents')

    # The "destination" category must contain transmittals
    dest_type = to_category.revision_class()
    if not issubclass(dest_type, OutgoingTransmittalRevision):
        raise errors.InvalidCategoryError(
            'Destination category must contain transmittals')

    # Do we have valid revisions?
    for rev in revisions:
        if not isinstance(rev, TransmittableMixin):
            raise errors.InvalidRevisionsError(
                'At least one of the revisions is invalid.')

        if not rev.can_be_transmitted:
            raise errors.InvalidRevisionsError(
                'At least one of the rivisions cannot be transmitted')
