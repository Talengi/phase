# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import factory
from factory import fuzzy

from accounts.factories import EntityFactory
from default_documents.models import (
    DemoMetadata, DemoMetadataRevision, ContractorDeliverable,
    ContractorDeliverableRevision)


CONTRACT_NB_CHOICES = (
    'FAC09001',
    'FAC10005'
)

DISCIPLINE_CHOICES = (
    'COM', 'CON', 'COR', 'DRI', 'MAI', 'MUL', 'OPE'
)

DOC_TYPE_CHOICES = (
    'PID', 'ANA', 'BAS', 'FAT', 'HAZ', 'ISO'
)


class MetadataFactory(factory.DjangoModelFactory):
    class Meta:
        model = DemoMetadata

    title = factory.SelfAttribute('document.title')


class MetadataRevisionFactory(factory.DjangoModelFactory):
    class Meta:
        model = DemoMetadataRevision

    docclass = 1
    revision = factory.sequence(lambda n: n + 1)
    received_date = datetime.date.today()
    return_code = fuzzy.FuzzyInteger(0, 5)

    @factory.post_generation
    def reviewers(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for reviewer in extracted:
                self.reviewers.add(reviewer)

    @factory.post_generation
    def document_revision(self, create, extracted, **kwargs):
        if self.revision > 1:
            self.metadata.latest_revision = self
            self.metadata.save()

            self.metadata.document.current_revision = self.revision
            self.metadata.document.save()


class ContractorDeliverableFactory(MetadataFactory):
    class Meta:
        model = ContractorDeliverable

    contract_number = fuzzy.FuzzyChoice(CONTRACT_NB_CHOICES)
    originator = factory.SubFactory(EntityFactory)
    unit = '000'
    discipline = fuzzy.FuzzyChoice(DISCIPLINE_CHOICES)
    document_type = fuzzy.FuzzyChoice(DOC_TYPE_CHOICES)
    sequential_number = factory.Sequence(lambda n: '{0:04}'.format(n))


class ContractorDeliverableRevisionFactory(MetadataRevisionFactory):
    class Meta:
        model = ContractorDeliverableRevision

    purpose_of_issue = 'FR'
