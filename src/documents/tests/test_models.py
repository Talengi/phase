from django.test import TestCase

from documents.models import Document
from documents.factories import DocumentFactory


class DocumentTest(TestCase):
    maxDiff = None

    def test_jsonification(self):
        """Tests that a jsonified document returns the appropriate values."""
        document = DocumentFactory(
            document_key='FAC09001-FWF-000-HSE-REP-0004',
            created_on='2013-04-20',
            current_revision_date='2013-04-20',
            metadata={
                'title': 'HAZOP report',
            },
            revision={
                'status': 'STD',
                'revision_date': '2013-04-20',
                'created_on': '2013-04-20',
                'updated_on': '2013-04-20',
            }
        )

        self.assertEqual(
            document.metadata.jsonified(),
            {
                'status': 'STD',
                'favorited': False,
                'title': 'HAZOP report',
                'url': '/documents/FAC09001-FWF-000-HSE-REP-0004/',
                'current_revision': u'1',
                'number': 'FAC09001-FWF-000-HSE-REP-0004',
                'current_revision_date': '2013-04-20',
                'pk': 1,
                'favorite_id': '',
                'document_key': 'FAC09001-FWF-000-HSE-REP-0004',
            }
        )
