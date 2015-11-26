# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from default_documents.tests.test import ContractorDeliverableTestCase
from documents.signals import revision_edited
from transmittals.factories import create_transmittal


class TransmittalUpdateTests(ContractorDeliverableTestCase):
    fixtures = ['initial_values_lists']

    def setUp(self):
        super(TransmittalUpdateTests, self).setUp()
        self.transmittal = create_transmittal()
        self.exported_revision = self.transmittal.exportedrevision_set.all()[0]
        self.revision = self.exported_revision.document.metadata.get_revision(
            self.exported_revision.revision)

    def test_initial_return_code(self):
        self.assertEqual('1', self.exported_revision.return_code)
        self.assertEqual('1', self.revision.return_code)

    def test_revision_update(self):
        """When a revision is modified, transmittal data is updated too."""
        self.revision.return_code = '4'
        self.revision.save()

        self.exported_revision.refresh_from_db()
        self.assertEqual('1', self.exported_revision.return_code)

        metadata = self.revision.document.metadata
        revision_edited.send(
            document=self.revision.document,
            metadata=metadata,
            revision=self.revision,
            sender=self.revision.__class__)

        self.exported_revision.refresh_from_db()
        self.assertEqual('4', self.exported_revision.return_code)
        self.assertEqual('4', self.revision.return_code)
