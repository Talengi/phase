from django.test import TestCase
from django.core.urlresolvers import reverse

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from accounts.factories import UserFactory


class ReviewListTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.client.login(email=self.user.email, password='pass')
        self.url = reverse('review_document_list')

    def test_empty_review_list(self):
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_review_not_started_yet(self):
        """If the review is not started yet, the doc does not appear in list."""
        doc = DocumentFactory(
            revision={
                'leader': self.user,
                'approver': self.user,
                'reviewers': [self.user],
            }
        )
        self.assertFalse(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_review_started(self):
        doc = DocumentFactory(
            revision={
                'leader': self.user,
                'approver': self.user,
                'reviewers': [self.user],
            }
        )
        doc.latest_revision.start_review()
        self.assertTrue(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')

    def test_review_finished(self):
        doc = DocumentFactory(
            revision={
                'leader': self.user,
                'approver': self.user,
                'reviewers': [self.user],
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_review()
        self.assertFalse(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')
