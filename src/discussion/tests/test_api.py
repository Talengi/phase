# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from accounts.factories import UserFactory
from discussion.factories import NoteFactory


class DiscussionApiAclTests(TestCase):

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
        self.doc.latest_revision.start_review()
        self.discussion_list_url = reverse('note-list', args=[self.doc.document_key, 1])

    def test_discussion_list_accepted(self):
        """Only the distribution list members can access the discussion."""
        res = self.client.get(self.discussion_list_url)
        self.assertEqual(res.status_code, 200)

    def test_discussion_list_forbidden(self):
        self.client.login(email=self.user2.email, password='pass')
        res = self.client.get(self.discussion_list_url)
        self.assertEqual(res.status_code, 403)

    def test_post_new_message_accepted(self):
        data = {
            'body': 'New message, yeah!'
        }
        res = self.client.post(self.discussion_list_url, data)
        self.assertEqual(res.status_code, 201)

    def test_post_new_message_forbidden(self):
        data = {
            'body': 'New message, yeah!'
        }
        self.client.login(email=self.user2.email, password='pass')
        res = self.client.post(self.discussion_list_url, data)
        self.assertEqual(res.status_code, 403)

    def test_update_existing_message_accepted(self):
        """The message owner can update it."""
        note = NoteFactory(
            document=self.doc,
            revision=1,
            author=self.user1
        )
        url = reverse('note-detail', args=[self.doc.document_key, 1, note.id])
        res = self.client.put(url, {'body': 'Update message'})
        self.assertEqual(res.status_code, 200)

    def test_update_existing_message_refused(self):
        """An user cannot update someone else's message."""
        note = NoteFactory(
            document=self.doc,
            revision=1,
            author=self.user2
        )
        url = reverse('note-detail', args=[self.doc.document_key, 1, note.id])
        res = self.client.put(url, {'body': 'Update message'})
        self.assertEqual(res.status_code, 403)

    def test_delete_existing_message_accepted(self):
        """The message owner can delete it"""
        note = NoteFactory(
            document=self.doc,
            revision=1,
            author=self.user1
        )
        url = reverse('note-detail', args=[self.doc.document_key, 1, note.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 204)

    def test_delete_existing_message_refused(self):
        """One cannot delete someone else's messages."""
        note = NoteFactory(
            document=self.doc,
            revision=1,
            author=self.user2
        )
        url = reverse('note-detail', args=[self.doc.document_key, 1, note.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 403)
