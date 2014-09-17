from django.test import TestCase
from django.core.urlresolvers import reverse

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory


enabled_review_button = '<button class="btn btn-warning" type="submit">Start review</button>'
disabled_review_button = '<button class="btn btn-warning disabled pull-right" type="button">Start review</button>'


class DocumentDetailTests(TestCase):
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
                'reviewers': [self.user],
                'leader': self.user,
                'approver': self.user,
            }
        )
        self.url = reverse("document_detail", args=[
            self.category.organisation.slug,
            self.category.slug,
            self.doc.document_key
        ])

    def test_start_review_button_is_preset(self):
        res = self.client.get(self.url)
        self.assertContains(res, enabled_review_button, html=True)

    def test_start_review_button_is_disabled_when_review_starts(self):
        self.doc.latest_revision.start_review()
        res = self.client.get(self.url)
        self.assertContains(res, disabled_review_button, html=True)

    def test_start_review_button_comes_back_when_review_is_canceled(self):
        self.doc.latest_revision.start_review()
        self.doc.latest_revision.cancel_review()
        res = self.client.get(self.url)
        self.assertContains(res, enabled_review_button, html=True)
