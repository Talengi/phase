from django.test import TestCase

from document_types.models import (
    ContractorDeliverable, ContractorDeliverableRevision)
from documents.factories import DocumentFactory


class ContractorDeliverableTests(TestCase):

    def test_document_number(self):
        """Tests that a document number is generated regularly."""
        document = DocumentFactory()
        revision = ContractorDeliverableRevision.objects.create(
            document=document
        )
        metadata = ContractorDeliverable.objects.create(
            document=document,
            latest_revision=revision,
            contract_number='FAC09001',
            title=u'HAZOP report',
            sequential_number="0004",
            discipline="HSE",
            document_type="REP",
        )
        self.assertEqual(metadata.document_key,
                         u'FAC09001-FWF-000-HSE-REP-0004')
        self.assertEqual(unicode(metadata),
                         u'FAC09001-FWF-000-HSE-REP-0004')
