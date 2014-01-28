import datetime
from django.test import TestCase
from django.utils.timezone import make_aware, utc

from documents.factories import DocumentFactory


class DocumentTest(TestCase):
    maxDiff = None

    def test_jsonification(self):
        """Tests that a jsonified document returns the appropriate values."""

        date = datetime.datetime(2013, 04, 20)
        date = make_aware(date, utc)

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
                'status': 'STD',
                'favorited': False,
                'title': 'HAZOP report',
                'url': '/documents/FAC09001-FWF-000-HSE-REP-0004/',
                'current_revision': u'1',
                'number': 'FAC09001-FWF-000-HSE-REP-0004',
                'current_revision_date': '2013-04-20 00:00:00+00:00',
                'pk': 1,
                'favorite_id': '',
                'document_key': 'FAC09001-FWF-000-HSE-REP-0004',
            }
        )
