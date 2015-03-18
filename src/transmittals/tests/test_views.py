# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils.html import escape

from documents.factories import DocumentFactory
from default_documents.models import ContractorDeliverable
from default_documents.factories import (
    ContractorDeliverableFactory, ContractorDeliverableRevisionFactory)
from categories.factories import CategoryFactory
from accounts.factories import UserFactory
from transmittals.factories import TransmittalFactory, TrsRevisionFactory
from transmittals.models import TrsRevision


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


class BaseTransmittalDiffViewTests(TestCase):

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

    def create_lines(self, nb_existing=1, nb_new=1, **kwargs):
        """Create `nb_existing` + `nb_new` lines in the transmittal."""
        doc = DocumentFactory(
            metadata_factory_class=ContractorDeliverableFactory,
            revision_factory_class=ContractorDeliverableRevisionFactory,
            category=self.category)
        metadata = doc.metadata

        arguments = {
            'transmittal': self.transmittal,
            'document': doc,
            'document_key': doc.document_key,
            'title': doc.title,
            'is_new_revision': False
        }
        arguments.update(kwargs)

        # Existing revisions
        for i in range(nb_existing):
            rev = ContractorDeliverableRevisionFactory(
                document=doc)

            arguments.update({'revision': rev.revision})
            TrsRevisionFactory(**arguments)

        metadata.latest_revision = rev
        metadata.save()

        arguments.update({'is_new_revision': True})

        # New revisions
        for i in range(nb_new):
            arguments.update({'revision': rev.revision + i + 1})
            TrsRevisionFactory(**arguments)

        return doc


class TransmittalDiffViewTests(BaseTransmittalDiffViewTests):

    def test_transmittal_detail_view(self):
        self.create_lines(2, 3)
        res = self.client.get(self.url)
        self.assertContains(res, 'tr class="document_row"', 5)

    def test_new_updated_labels(self):
        self.create_lines(3, 4)
        res = self.client.get(self.url)
        self.assertContains(res, 'span class="label label-warning"', 4)
        self.assertContains(res, 'span class="label label-primary"', 3)

    def test_accepted_icons(self):
        self.create_lines(1, 1)
        self.create_lines(2, 2, accepted=True)
        self.create_lines(3, 3, accepted=False)

        res = self.client.get(self.url)
        self.assertContains(res, 'glyphicon-empty', 2)
        # "+ 2" because there are icons elsewhere in the page
        self.assertContains(res, 'glyphicon-ok', 4 + 2)
        self.assertContains(res, 'glyphicon-remove', 6 + 1)


class TrsRevisionDiffViewTests(BaseTransmittalDiffViewTests):

    def setUp(self):
        super(TrsRevisionDiffViewTests, self).setUp()
        self.doc = self.create_lines(1, 2)
        self.trs_revisions = self.transmittal.trsrevision_set.all()

    def test_diff_with_existing_revision(self):
        trs_revision = self.trs_revisions[0]
        trs_revision.title = 'New title yeah!'
        trs_revision.save()
        revision = self.doc.metadata.get_revision(trs_revision.revision)

        res = self.client.get(trs_revision.get_absolute_url())
        self.assertContains(res, escape(revision.title()))
        self.assertContains(res, trs_revision.title)

    def test_diff_with_single_new_revision(self):
        trs_revision = self.trs_revisions[1]
        trs_revision.title = 'New title yeah!'
        trs_revision.save()
        revision = self.doc.metadata.latest_revision

        res = self.client.get(trs_revision.get_absolute_url())
        self.assertContains(res, escape(revision.title()))
        self.assertContains(res, trs_revision.title)

    def test_diff_with_new_revisions(self):
        new_revision = self.trs_revisions[1]
        new_revision.title = 'Old title yeah!'
        new_revision.save()

        newest_revision = self.trs_revisions[2]
        newest_revision.title = 'New title yeah!'
        newest_revision.save()

        res = self.client.get(newest_revision.get_absolute_url())
        self.assertContains(res, new_revision.title)
        self.assertContains(res, newest_revision.title)

    def test_accept_changes(self):
        trs_revision = self.trs_revisions[0]
        self.assertIsNone(trs_revision.accepted)

        self.client.post(trs_revision.get_absolute_url(), {'accept': 'accept'})
        trs_revision = TrsRevision.objects.get(pk=trs_revision.pk)
        self.assertTrue(trs_revision.accepted)

    def test_refuse_changes(self):
        trs_revision = self.trs_revisions[0]
        self.assertIsNone(trs_revision.accepted)

        self.client.post(trs_revision.get_absolute_url(), {'refuse': 'refuse'})
        trs_revision = TrsRevision.objects.get(pk=trs_revision.pk)
        self.assertFalse(trs_revision.accepted)

    def test_leave_comment(self):
        trs_revision = self.trs_revisions[0]
        self.assertIsNone(trs_revision.comment)

        self.client.post(trs_revision.get_absolute_url(), {
            'accept': 'accept',
            'comment': 'Gloubiboulga'
        })
        trs_revision = TrsRevision.objects.get(pk=trs_revision.pk)
        self.assertEqual(trs_revision.comment, 'Gloubiboulga')
