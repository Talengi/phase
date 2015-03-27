# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import factory

from documents.factories import DocumentFactory
from transmittals.models import Transmittal, TransmittalRevision, TrsRevision


class TransmittalRevisionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = TransmittalRevision


class TransmittalFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Transmittal

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
    FACTORY_FOR = TrsRevision

    transmittal = factory.SubFactory(TransmittalFactory)
    document_key = 'FAC10005-CTR-000-EXP-LAY-4891'
    title = factory.Sequence(lambda n: 'Trs Revision {0:05}'.format(n))
    revision = factory.Sequence(lambda n: n)
    is_new_revision = True
