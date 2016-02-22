# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.utils.timezone import utc

from documents.factories import DocumentFactory
from accounts.models import User
from accounts.factories import UserFactory


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
                u'document_number': 'FAC09001-FWF-000-HSE-REP-0004',
            }
        )

    def test_get_actions(self):
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

        user = UserFactory()
        metadata = document.metadata
        metadata_revision = document.latest_revision
        actions = metadata_revision.get_actions(metadata, user)
        self.assertEqual(len(actions), 0)
        change_doc_perm = Permission.objects.get(
            codename='change_document')
        can_control_perm = Permission.objects.get(
            codename='can_control_document')
        user.user_permissions.add(change_doc_perm)
        user.user_permissions.add(can_control_perm)
        # Refresh object
        user = User.objects.get(pk=user.pk)
        actions = metadata_revision.get_actions(metadata, user)
        # Actions must contain 3 MenuItem and a DividerMenuItem
        self.assertEqual(len(actions), 4)
