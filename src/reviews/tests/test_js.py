# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.contrib.contenttypes.models import ContentType

from casper.tests import CasperTestCase

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from default_documents.models import ContractorDeliverable
from default_documents.factories import (
    ContractorDeliverableFactory, ContractorDeliverableRevisionFactory)
from reviews.factories import DistributionListFactory


class DistributionListWidgetTestDistributionListWidgetTests(CasperTestCase):
    def setUp(self):
        Model = ContentType.objects.get_for_model(ContractorDeliverable)
        self.category = CategoryFactory(
            category_template__metadata_model=Model)
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(email=self.user.email, password='pass')
        self.doc = DocumentFactory(
            category=self.category,
            metadata_factory_class=ContractorDeliverableFactory,
            revision_factory_class=ContractorDeliverableRevisionFactory,
        )
        url = self.doc.get_edit_url()
        self.url = '%s%s' % (self.live_server_url, url)
        self.test_file = os.path.join(
            os.path.dirname(__file__),
            'casper_tests',
            'tests.js'
        )

    def test_select_distribution_list(self):
        dl = DistributionListFactory(
            categories=[self.category],
            name='Team Cassoulet',
        )
        DistributionListFactory(
            categories=[self.category],
            name='Team Oui Oui et ses potes')

        self.assertTrue(self.casper(
            self.test_file,
            url=self.url,
            leader_id=dl.leader_id,
            approver_id=dl.approver_id,
        ))
