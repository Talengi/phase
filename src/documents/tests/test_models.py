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
                u'status': u'STD',
                u'title': u'HAZOP report',
                u'url': '/documents/FAC09001-FWF-000-HSE-REP-0004/',
                u'current_revision': u'01',
                u'current_revision_date': datetime.date(2013, 4, 20),
                u'pk': 1,
                u'document_pk': 1,
                u'document_key': u'FAC09001-FWF-000-HSE-REP-0004',
            }
        )
