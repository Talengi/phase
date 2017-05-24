# -*- coding: utf-8 -*-



from django.test import TestCase

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from accounts.factories import UserFactory
from discussion.utils import get_discussion_length
from discussion.factories import NoteFactory
from discussion.models import Note


class NoteTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user1 = UserFactory(
            username='user1',
            category=self.category
        )
        self.user2 = UserFactory(
            username='user2',
            category=self.category
        )
        self.user3 = UserFactory(
            username='user-3_username',
            category=self.category
        )
        self.doc = DocumentFactory(
            revision={
                'leader': self.user1,
            }
        )
        self.revision = self.doc.latest_revision
        self.revision.start_review()

    def create_note(self, body):
        return NoteFactory(
            body=body,
            document=self.doc,
            author=self.user1,
            revision=1
        )

    def test_parse_single_mention(self):
        note = self.create_note('bla bla bla @user1 bla bla')
        self.assertEqual(note.parse_mentions(), [self.user1])

    def test_parse_single_mention_beginning(self):
        note = self.create_note('@user1 bla bla bla bla')
        self.assertEqual(note.parse_mentions(), [self.user1])

    def test_parse_multiple_mentions(self):
        note = self.create_note('bla bla @user1 bla bla @user2 bla bla')
        mentions = note.parse_mentions()
        self.assertTrue(self.user1 in mentions)
        self.assertTrue(self.user2 in mentions)
        self.assertEqual(len(mentions), 2)

    def test_parse_duplicate_mentions(self):
        note = self.create_note('bla bla @user1 bla bla @user2 bla bla @user2')
        self.assertEqual(note.parse_mentions(), [self.user1, self.user2])

    def test_parse_mentions_with_hyphens(self):
        note = self.create_note('bla bla @user-3_username bla bla')
        self.assertEqual(note.parse_mentions(), [self.user3])

    def test_parse_no_mentions(self):
        note = self.create_note('bal bla bla bla bla')
        self.assertEqual(note.parse_mentions(), [])

    def test_parse_wrong_mentions(self):
        note = self.create_note('bal bla bla bla bla @user42 bla bla')
        self.assertEqual(note.parse_mentions(), [])

    def test_parse_wrong_mentions_2(self):
        note = self.create_note('bal bla bla bla bla @user111 bla bla')
        self.assertEqual(note.parse_mentions(), [])

    def test_parse_incomplete_mention(self):
        note = self.create_note('bal bla bla bla bla @use bla bla')
        self.assertEqual(note.parse_mentions(), [])


class CacheTests(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user1 = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.client.login(email=self.user1.email, password='pass')
        self.doc = DocumentFactory(
            revision={
                'leader': self.user1,
            }
        )
        self.revision = self.doc.latest_revision
        self.revision.start_review()

    def test_empty_discussion(self):
        self.assertEqual(get_discussion_length(self.revision), 0)

    def test_new_remarks_update_cache(self):
        for _ in range(10):
            NoteFactory(
                author=self.user1,
                document=self.doc,
                revision=self.revision.revision,
            )
        self.assertEqual(get_discussion_length(self.revision), 10)

    def test_delete_remarks_update_cache(self):
        note = NoteFactory(
            author=self.user1,
            document=self.doc,
            revision=self.revision.revision)
        self.assertEqual(get_discussion_length(self.revision), 1)
        note.delete()
        self.assertEqual(get_discussion_length(self.revision), 0)

    def test_cancel_review_updates_cache(self):
        for _ in range(10):
            NoteFactory(
                author=self.user1,
                document=self.doc,
                revision=self.revision.revision,
            )
        self.revision.cancel_review()
        self.assertEqual(get_discussion_length(self.revision), 0)


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
                'leader': self.user1,
            }
        )
        self.revision = self.doc.latest_revision
        self.revision.start_review()

    def test_notes_are_deleted_when_review_is_canceled(self):
        for _ in range(10):
            NoteFactory(
                author=self.user1,
                document=self.doc,
                revision=1
            )
        self.assertEqual(Note.objects.all().count(), 10)

        self.revision.cancel_review()
        self.assertEqual(Note.objects.all().count(), 0)
