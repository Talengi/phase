# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from accounts.factories import UserFactory
from discussion.factories import NoteFactory
from discussion.models import Note


class ReviewTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user1 = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.client.login(email=self.user1.email, password='pass')
        self.user2 = UserFactory(
            email='otheruser@phase.fr',
            password='pass',
            category=self.category
        )
        self.doc = DocumentFactory(
            revision={
                'reviewers': [self.user1],
                'leader': self.user1,
                'approver': self.user1,
            }
        )
        self.revision = self.doc.latest_revision
        self.revision.start_review()

    def test_notes_are_deleted_when_review_is_canceled(self):
        for _ in xrange(10):
            NoteFactory(
                author=self.user1,
                document=self.doc,
                revision=1
            )
        self.assertEqual(Note.objects.all().count(), 10)

        self.revision.cancel_review()
        self.assertEqual(Note.objects.all().count(), 0)
