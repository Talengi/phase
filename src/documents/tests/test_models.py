import datetime
from django.test import TestCase
from django.utils.timezone import utc

from documents.factories import DocumentFactory


class DocumentTest(TestCase):
    maxDiff = None

    def test_metadata_property(self):
        date = datetime.datetime(2013, 04, 20, 12, 0, 0, tzinfo=utc)
        document = DocumentFactory(
            document_key='FAC09001-FWF-000-HSE-REP-0004',
            created_on=date,
            current_revision_date=date,
            metadata={
                'title': 'HAZOP report',
            },
            revision={
                'status': 'STD',
                'revision_date': date,
                'created_on': date,
                'updated_on': date,
            }
        )
        metadata = document.metadata
        self.assertEqual(metadata.title, 'HAZOP report')

    def test_jsonification(self):
        """Tests that a jsonified document returns the appropriate values."""

        date = datetime.datetime(2013, 04, 20, 12, 0, 0, tzinfo=utc)

        document = DocumentFactory(
            document_key='FAC09001-FWF-000-HSE-REP-0004',
            created_on=date,
            current_revision_date=date,
            metadata={
                'title': 'HAZOP report',
            },
            revision={
                'status': 'STD',
                'revision_date': date,
                'created_on': date,
                'updated_on': date,
            }
        )

        self.assertEqual(
            document.metadata.jsonified(),
            {
                'status': u'STD',
                'favorited': False,
                'title': u'HAZOP report',
                'url': '/documents/FAC09001-FWF-000-HSE-REP-0004/',
                'current_revision': u'01',
                'number': u'FAC09001-FWF-000-HSE-REP-0004',
                'current_revision_date': u'2013-04-20',
                'pk': 1,
                'favorite_id': '',
                'document_pk': 1,
                'document_key': u'FAC09001-FWF-000-HSE-REP-0004',
            }
        )
