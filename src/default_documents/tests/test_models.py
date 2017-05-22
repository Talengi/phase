# -*- coding: utf-8 -*-


from default_documents.tests.test import ContractorDeliverableTestCase

from accounts.factories import EntityFactory


class DocumentKeyTests(ContractorDeliverableTestCase):

    def test_document_number(self):
        """Tests that a document number is generated regularly."""
        kwargs = {
            'metadata': {
                'contract_number': 'FAC09001',
                'title': 'HAZOP report',
                'originator': EntityFactory(trigram='FWF'),
                'sequential_number': '0004',
                'discipline': 'HSE',
                'document_type': 'REP',
            }
        }
        doc = self.create_doc(**kwargs)

        self.assertEqual(doc.metadata.generate_document_key(),
                         'FAC09001-FWF-000-HSE-REP-0004')
