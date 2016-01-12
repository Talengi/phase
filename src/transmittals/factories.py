# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from django.contrib.contenttypes.models import ContentType

import factory

from documents.factories import DocumentFactory
from accounts.factories import EntityFactory
from categories.factories import CategoryFactory
from default_documents.models import ContractorDeliverable
from default_documents.factories import (
    ContractorDeliverableFactory, ContractorDeliverableRevisionFactory)
from transmittals.models import (
    Transmittal, TransmittalRevision, TrsRevision, OutgoingTransmittal,
    OutgoingTransmittalRevision)


class TransmittalRevisionFactory(factory.DjangoModelFactory):
    class Meta:
        model = TransmittalRevision

    received_date = datetime.date.today()
    revision = factory.sequence(lambda n: n + 1)


class TransmittalFactory(factory.DjangoModelFactory):
    class Meta:
        model = Transmittal

    contractor = 'test'
    tobechecked_dir = '/tmp/test_ctr_clt/tobechecked/'
    accepted_dir = '/tmp/test_ctr_clt/accepted/'
    rejected_dir = '/tmp/test_ctr_clt/rejected/'
    contract_number = 'FAC10005'
    originator = 'CTR'
    recipient = 'CLT'
    sequential_number = factory.Sequence(lambda n: n + 1)
    document_key = factory.Sequence(lambda n: 'transmittal-{}'.format(n))
    document = factory.SubFactory(
        DocumentFactory,
        document_key=factory.SelfAttribute('..document_key'))
    latest_revision = factory.SubFactory(
        TransmittalRevisionFactory,
        document=factory.SelfAttribute('..document'))


class TrsRevisionFactory(factory.DjangoModelFactory):
    class Meta:
        model = TrsRevision

    transmittal = factory.SubFactory(TransmittalFactory)
    document_key = 'FAC10005-CTR-000-EXP-LAY-4891'
    title = factory.Sequence(lambda n: 'Trs Revision {0:05}'.format(n))
    revision = factory.Sequence(lambda n: n)
    is_new_revision = True
    received_date = datetime.date.today()


class OutgoingTransmittalRevisionFactory(factory.DjangoModelFactory):
    class Meta:
        model = OutgoingTransmittalRevision


class OutgoingTransmittalFactory(factory.DjangoModelFactory):
    class Meta:
        model = OutgoingTransmittal

    contract_number = 'FAC10005'
    originator = 'CTR'
    recipient = 'CLT'
    sequential_number = factory.Sequence(lambda n: n + 1)
    document = factory.SubFactory(
        DocumentFactory,
        document_key=factory.SelfAttribute('..document_key'))
    revisions_category = factory.SubFactory(CategoryFactory)
    latest_revision = factory.SubFactory(
        TransmittalRevisionFactory,
        document=factory.SelfAttribute('..document'))


def create_transmittal():
    """Create a test transmittal with a few documents linked."""

    # Create documents
    CDModel = ContentType.objects.get_for_model(ContractorDeliverable)
    entity = EntityFactory()
    deliverables_category = CategoryFactory(
        category_template__metadata_model=CDModel,
        third_parties=[entity])

    data = {
        'category': deliverables_category,
        'revision': {
            'return_code': 1
        },
        'metadata_factory_class': ContractorDeliverableFactory,
        'revision_factory_class': ContractorDeliverableRevisionFactory,
    }
    revisions = []
    for _ in range(10):
        doc = DocumentFactory(**data)
        revisions.append(doc.latest_revision)

    # Create the actual transmittal
    OutgoingTransmittalModel = ContentType.objects.get_for_model(
        OutgoingTransmittal)
    transmittal_category = CategoryFactory(
        category_template__metadata_model=OutgoingTransmittalModel)
    data = {
        'category': transmittal_category,
        'metadata': {
            'originator': 'CTR',
            'recipient': entity,
            'contract_number': 'FAC10005',
        },
        'metadata_factory_class': OutgoingTransmittalFactory,
        'revision_factory_class': OutgoingTransmittalRevisionFactory,
    }
    doc = DocumentFactory(**data)
    transmittal = doc.metadata
    transmittal.link_to_revisions(revisions)
    return transmittal
