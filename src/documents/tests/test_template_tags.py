# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
from django.test import TestCase
from pytz import utc

from ..templatetags.private import download_link, short_download_link
from ..factories import DocumentFactory


class DocumentDetailTests(TestCase):

    def setUp(self):
        super(DocumentDetailTests, self).setUp()
        date = datetime.datetime(2013, 4, 20, 12, 0, 0, tzinfo=utc)
        self.file_name = 'some-long-file-name-to-download.pdf'
        self.document = DocumentFactory(
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
                'native_file': self.file_name
            }
        )

    def test_download_link_tag(self):
        rev = self.document.latest_revision
        link = download_link(rev, 'native_file')
        self.assertTrue(self.file_name in link)

    def test_short_download_link_tag(self):
        rev = self.document.latest_revision
        link = short_download_link(rev, 'native_file')
        self.assertTrue('{:.10}…'.format(self.file_name) in link)
