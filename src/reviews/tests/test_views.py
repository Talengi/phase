from django.test import TestCase
from django.core.urlresolvers import reverse

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from accounts.factories import UserFactory


class ReviewersDocumentListTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.other_user = UserFactory(
            email='test@phase.fr',
            category=self.category
        )
        self.client.login(email=self.user.email, password='pass')
        self.url = reverse('reviewers_review_document_list')

    def test_empty_review_list(self):
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_review_not_started_yet(self):
        """If the review is not started yet, the doc does not appear in list."""
        doc = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'approver': self.other_user,
            }
        )
        self.assertFalse(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_review_started(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.user,
                'approver': self.user,
            }
        )
        doc.latest_revision.start_review()
        self.assertTrue(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')

    def test_step_finished(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.user,
                'approver': self.user,
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_reviewers_step()
        self.assertTrue(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_review_finished(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.user,
                'approver': self.user,
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_review()
        self.assertFalse(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')


class LeaderDocumentListTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.other_user = UserFactory(
            email='test@phase.fr',
            category=self.category
        )
        self.client.login(email=self.user.email, password='pass')
        self.url = reverse('leader_review_document_list')

    def test_empty_review_list(self):
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_review_not_started_yet(self):
        """If the review is not started yet, the doc does not appear in list."""
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.user,
                'approver': self.other_user,
            }
        )
        self.assertFalse(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_previous_step(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.user,
                'approver': self.other_user,
            }
        )
        doc.latest_revision.start_review()
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')

    def test_current_step(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.user,
                'approver': self.other_user,
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_reviewers_step()
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')

    def test_step_finished(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.user,
                'approver': self.other_user,
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_leader_step()
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')


class ApproverDocumentListTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.other_user = UserFactory(
            email='test@phase.fr',
            category=self.category
        )
        self.client.login(email=self.user.email, password='pass')
        self.url = reverse('approver_review_document_list')

    def test_previous_step(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.other_user,
                'approver': self.user,
            }
        )
        doc.latest_revision.start_review()
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')

        doc.latest_revision.end_reviewers_step()
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')

    def test_current_step(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.other_user,
                'approver': self.user,
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_leader_step()
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')

    def test_step_finished(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.other_user,
                'approver': self.user,
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_review()
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')
