# -*- coding: utf-8 -*-


from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from accounts.factories import UserFactory, EntityFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from default_documents.models import ContractorDeliverable
from default_documents.factories import (
    ContractorDeliverableFactory, ContractorDeliverableRevisionFactory)


class ContractorDeliverableTestCase(TestCase):
    """Base test case class with useful document helpers."""

    def setUp(self):
        Model = ContentType.objects.get_for_model(ContractorDeliverable)
        self.entity = EntityFactory()
        self.category = CategoryFactory(
            category_template__metadata_model=Model,
            third_parties=[self.entity])
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(email=self.user.email, password='pass')

    def create_doc(self, **kwargs):
        kwargs.update({
            'category': self.category,
            'metadata_factory_class': ContractorDeliverableFactory,
            'revision_factory_class': ContractorDeliverableRevisionFactory,
        })
        doc = DocumentFactory(**kwargs)
        return doc
