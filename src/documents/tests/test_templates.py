from django.test import TestCase
from django.core.urlresolvers import reverse

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory


review_button = '<a href="#" class="dropdown-submit">Start review</a>'


class DocumentDetailTests(TestCase):
    """Test buttons presence for an admin / doc controller"""
    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            name='User',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(username=self.user.email, password='pass')
        self.doc = DocumentFactory(
            category=self.category,
            revision={
                'leader': self.user,
            }
        )
        self.url = reverse("document_detail", args=[
            self.category.organisation.slug,
            self.category.slug,
            self.doc.document_key
        ])

    def test_review_not_started(self):
        res = self.client.get(self.url)
        self.assertContains(res, review_button, html=True)
        self.assertNotContains(res, 'Cancel review')

    def test_review_started(self):
        self.doc.latest_revision.start_review()
        res = self.client.get(self.url)
        print res
        self.assertNotContains(res, review_button, html=True)
        self.assertContains(res, 'Cancel review')

    def test_review_canceled(self):
        self.doc.latest_revision.start_review()
        self.doc.latest_revision.cancel_review()
        res = self.client.get(self.url)
        self.assertContains(res, review_button, html=True)
        self.assertNotContains(res, 'Cancel review')


class SimpleUserDocumentDetailTests(TestCase):
    """Simple users cannot start reviews."""

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            name='User',
            password='pass',
            is_superuser=False,
            category=self.category)
        self.client.login(username=self.user.email, password='pass')
        self.doc = DocumentFactory(
            category=self.category,
            revision={
                'leader': self.user,
            }
        )
        self.url = reverse("document_detail", args=[
            self.category.organisation.slug,
            self.category.slug,
            self.doc.document_key
        ])

    def test_start_review_button_is_present(self):
        res = self.client.get(self.url)
        self.assertNotContains(res, review_button, html=True)

    def test_cancel_review_button(self):
        res = self.client.get(self.url)
        self.assertNotContains(res, 'Cancel review')

        self.doc.latest_revision.start_review()
        res = self.client.get(self.url)
        self.assertNotContains(res, 'Cancel review')
