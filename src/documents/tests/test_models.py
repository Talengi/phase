# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
            document.to_json(),
            {
                u'status': u'STD',
                u'title': u'HAZOP report',
                u'url': document.get_absolute_url(),
                u'revision': 1,
                u'is_latest_revision': True,
                u'pk': document.metadata.latest_revision.pk,
                u'document_pk': document.pk,
                u'metadata_pk': document.metadata.pk,
                u'document_key': 'FAC09001-FWF-000-HSE-REP-0004',
            }
        )
