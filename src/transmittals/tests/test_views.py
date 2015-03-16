# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from documents.factories import DocumentFactory
from default_documents.models import ContractorDeliverable
from default_documents.factories import (
    ContractorDeliverableFactory, ContractorDeliverableRevisionFactory)
from categories.factories import CategoryFactory
from accounts.factories import UserFactory
from transmittals.factories import TransmittalFactory, TrsRevisionFactory


class TransmittalListTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(email=user.email, password='pass')
        self.url = reverse('transmittal_list')

    def test_empty_transmittal_list(self):
        res = self.client.get(self.url)
        self.assertContains(res, 'There are no transmittals here')

    def test_transmittal_list(self):
        TransmittalFactory()
        TransmittalFactory()
        TransmittalFactory()
        res = self.client.get(self.url)
        self.assertNotContains(res, 'There are no transmittals here')
        self.assertContains(res, 'tr class="document_row"', 3)


class TransmittalDiffViewTests(TestCase):

    def setUp(self):
        Model = ContentType.objects.get_for_model(ContractorDeliverable)
        self.category = CategoryFactory(category_template__metadata_model=Model)
        self.transmittal = TransmittalFactory()
        user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(email=user.email, password='pass')
        self.url = self.transmittal.get_absolute_url()

    def create_lines(self, nb_existing=1, nb_new=1):
        """Create `nb_existing` + `nb_new` lines in the transmittal."""
        doc = DocumentFactory(
            metadata_factory_class=ContractorDeliverableFactory,
            revision_factory_class=ContractorDeliverableRevisionFactory,
            category=self.category)

        # Existing revisions
        for i in range(nb_existing):
            rev = ContractorDeliverableRevisionFactory(
                document=doc)

            TrsRevisionFactory(
                transmittal=self.transmittal,
                document=doc,
                document_key=doc.document_key,
                title=doc.title,
                revision=rev.revision,
                is_new_revision=False)

        # New revisions
        for i in range(nb_new):
            TrsRevisionFactory(
                transmittal=self.transmittal,
                document=doc,
                document_key=doc.document_key,
                title=doc.title,
                revision=rev.revision + i,
                is_new_revision=True)

    def test_transmittal_detail_view(self):
        self.create_lines(2, 3)
        res = self.client.get(self.url)
        self.assertContains(res, 'tr class="document_row"', 5)
