# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework.test import APIClient

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from accounts.factories import UserFactory
from discussion.factories import NoteFactory
from discussion.models import Note


class BaseDiscussionAclTests(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user1 = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.user2 = UserFactory(
            email='otheruser@phase.fr',
            password='pass',
            category=self.category
        )
        self.user3 = UserFactory(email='thirduser@phase.fr', password='pass')
        self.doc = DocumentFactory(
            category=self.category,
            revision={
                'reviewers': [self.user1],
                'leader': self.user1,
                'approver': self.user1,
            }
        )
        self.client = APIClient()
        self.client.login(email=self.user1.email, password='pass')
        self.doc.latest_revision.start_review()
        self.discussion_list_url = reverse('note-list', args=[self.doc.document_key, 1])


class DiscussionListGet(BaseDiscussionAclTests):
    """Test the read permisssions on the discussion."""

    def test_distribution_list_member(self):
        """All distribution list members can access the discussion."""
        res = self.client.get(self.discussion_list_url)
        self.assertEqual(res.status_code, 200)

    def test_category_member(self):
        """All members with access to the document can see the discussion."""
        self.client.login(email=self.user2.email, password='pass')
        res = self.client.get(self.discussion_list_url)
        self.assertEqual(res.status_code, 200)

    def test_foreign_user(self):
        self.client.login(email=self.user3.email, password='pass')
        res = self.client.get(self.discussion_list_url)
        self.assertEqual(res.status_code, 403)


class DiscussionListPost(BaseDiscussionAclTests):
    """Test the new discussion item creation permission."""

    def test_distribution_list_member(self):
        data = {
            'body': 'New message, yeah!'
        }
        res = self.client.post(self.discussion_list_url, data)
        self.assertEqual(res.status_code, 201)

    def test_category_member(self):
        data = {
            'body': 'New message, yeah!'
        }
        self.client.login(email=self.user2.email, password='pass')
        res = self.client.post(self.discussion_list_url, data)
        self.assertEqual(res.status_code, 403)

    def test_foreign_user(self):
        data = {
            'body': 'New message, yeah!'
        }
        self.client.login(email=self.user3.email, password='pass')
        res = self.client.post(self.discussion_list_url, data)
        self.assertEqual(res.status_code, 403)


class DiscussionItemPut(BaseDiscussionAclTests):
    """Test the discussion item update permission."""

    def test_message_owner(self):
        """The message owner can update it."""
        note = NoteFactory(
            document=self.doc,
            revision=1,
            author=self.user1
        )
        url = reverse('note-detail', args=[self.doc.document_key, 1, note.id])
        res = self.client.put(url, {'body': 'Update message'})
        self.assertEqual(res.status_code, 200)

    def test_other_user(self):
        """An user cannot update someone else's message."""
        note = NoteFactory(
            document=self.doc,
            revision=1,
            author=self.user2
        )
        url = reverse('note-detail', args=[self.doc.document_key, 1, note.id])
        res = self.client.put(
            url,
            {'body': 'Update message'},
            content_type='application/json')
        self.assertEqual(res.status_code, 403)


class DiscussionItemDelete(BaseDiscussionAclTests):
    """Test the discussion item delete permission."""

    def test_message_owner(self):
        """The message owner can delete it"""
        note = NoteFactory(
            document=self.doc,
            revision=1,
            author=self.user1
        )
        self.assertIsNone(note.deleted_on)
        url = reverse('note-detail', args=[self.doc.document_key, 1, note.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 204)

        note = Note.objects.get(pk=note.pk)
        self.assertIsNotNone(note.deleted_on)

    def test_other_user(self):
        """One cannot delete someone else's messages."""
        note = NoteFactory(
            document=self.doc,
            revision=1,
            author=self.user2
        )
        url = reverse('note-detail', args=[self.doc.document_key, 1, note.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 403)
