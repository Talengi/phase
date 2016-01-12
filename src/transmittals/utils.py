# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Max
from django.utils import timezone
from django.db import transaction

from documents.utils import save_document_forms
from transmittals import errors
from transmittals.models import (
    OutgoingTransmittal, OutgoingTransmittalRevision, TransmittableMixin)
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


def create_transmittal(from_category, to_category, revisions, contract_nb,
                       recipient, **form_data):
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

    # The recipient must be linked to the "from" category
    if from_category not in recipient.linked_categories.all():
        raise errors.InvalidRecipientError(
            'Recipient is not linked to the document category')

    # Do we have valid revisions?
    for rev in revisions:
        if not isinstance(rev, TransmittableMixin):
            raise errors.InvalidRevisionsError(
                'At least one of the revisions is invalid.')

        if not rev.can_be_transmitted:
            raise errors.InvalidRevisionsError(
                'At least one of the rivisions cannot be transmitted')

        if not rev.document.category == from_category:
            raise errors.InvalidRevisionsError(
                'Some revisions are not from the correct category')

    originator = from_category.organisation.trigram
    sequential_number = find_next_trs_number(originator, recipient, contract_nb)
    form_data.update({
        'revisions_category': from_category,
        'contract_number': contract_nb,
        'originator': originator,
        'recipient': recipient.id,
        'sequential_number': sequential_number,
        'created_on': timezone.now(),
        'received_date': timezone.now(),
    })

    # Let's create the transmittal, then
    trs_form = OutgoingTransmittalForm(form_data, category=to_category)
    revision_form = OutgoingTransmittalRevisionForm(form_data, category=to_category)

    with transaction.atomic():
        doc, trs, revision = save_document_forms(trs_form, revision_form, to_category)
        trs.link_to_revisions(revisions)
    return doc, trs, revision


def find_next_trs_number(originator, recipient, contract_nb):
    """Returns the first available transmittal sequential number."""
    qs = OutgoingTransmittal.objects \
        .filter(originator=originator) \
        .filter(recipient=recipient) \
        .filter(contract_number=contract_nb) \
        .aggregate(Max('sequential_number'))
    max_nb = qs.get('sequential_number__max')
    return max_nb + 1 if max_nb else 1
