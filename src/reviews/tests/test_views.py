# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import json

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from accounts.factories import UserFactory
from reviews.models import Review


class BatchReviewTests(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.client.login(email=self.user.email, password='pass')
        self.url = reverse('batch_start_reviews', args=[
            self.category.organisation.slug,
            self.category.slug,
        ])
        self.list_url = reverse('category_document_list', args=[
            self.category.organisation.slug,
            self.category.slug,
        ])
        self.doc1 = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.user,
                'approver': self.user,
                'received_date': datetime.date.today(),
            }
        )
        self.doc2 = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.user,
                'approver': self.user,
                'received_date': datetime.date.today(),
            }
        )
        self.doc3 = DocumentFactory(
            revision={
                'reviewers': [],
                'leader': None,
                'approver': None,
                'received_date': datetime.date.today(),
            }
        )
        self.ok = 'The review started for the following documents'
        self.nok = "We failed to start the review for the following documents"

    def test_batch_review_returns_poll_url(self):
        res = self.client.post(
            self.url,
            {'document_ids': [self.doc1.id, self.doc2.id]}
        )
        json_content = json.loads(res.content)
        self.assertTrue('poll_url' in json_content)


class PrioritiesDocumentListTests(TestCase):

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
        self.url = reverse('priorities_review_document_list')

    def test_empty_review_list(self):
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')
        self.assertNotContains(res, 'Close reviews')

    def test_non_prioritary_document(self):
        """User is not approver nor leader."""
        doc = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'docclass': 1,
                'received_date': datetime.date.today(),
            }
        )
        doc.latest_revision.start_review()
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_non_prioritary_document2(self):
        """Due date > 5 days."""
        doc = DocumentFactory(
            revision={
                'leader': self.user,
                'docclass': 1,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.review_due_date = timezone.now() + datetime.timedelta(days=6)
        revision.save()
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_non_prioritary_document3(self):
        """docclass < 2"""
        doc = DocumentFactory(
            revision={
                'leader': self.user,
                'docclass': 3,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.review_due_date = timezone.now()
        revision.save()
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_prioritary_document(self):
        doc = DocumentFactory(
            revision={
                'leader': self.user,
                'docclass': 1,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        due_date = timezone.now() + datetime.timedelta(days=1)
        revision.start_review(due_date=due_date)
        self.assertTrue(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')


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
        self.assertContains(res, 'Close reviews')

    def test_review_not_started_yet(self):
        """If the review is not started yet, the doc does not appear in list."""
        doc = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'received_date': datetime.date.today(),
            }
        )
        self.assertFalse(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_review_started(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'received_date': datetime.date.today(),
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
                'leader': self.other_user,
                'received_date': datetime.date.today(),
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
                'leader': self.other_user,
                'received_date': datetime.date.today(),
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_review()
        self.assertFalse(doc.latest_revision.is_under_review())
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')

    def test_review_done(self):
        doc = DocumentFactory(
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'received_date': datetime.date.today(),
            }
        )
        doc.latest_revision.start_review()
        self.assertTrue(doc.latest_revision.is_under_review())
        Review.objects \
            .filter(document=doc) \
            .filter(revision=doc.latest_revision.revision) \
            .filter(reviewer=self.user) \
            .update(closed_on=timezone.now())

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
        self.assertNotContains(res, 'Close reviews')

    def test_review_not_started_yet(self):
        """If the review is not started yet, the doc does not appear in list."""
        doc = DocumentFactory(
            revision={
                'reviewers': [self.other_user],
                'leader': self.user,
                'received_date': datetime.date.today(),
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
                'received_date': datetime.date.today(),
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
                'received_date': datetime.date.today(),
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
                'received_date': datetime.date.today(),
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

    def test_empty_review_list(self):
        res = self.client.get(self.url)
        self.assertNotContains(res, 'Close reviews')

    def test_previous_step(self):
        doc = DocumentFactory(
            revision={
                'leader': self.other_user,
                'approver': self.user,
                'received_date': datetime.date.today(),
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
                'leader': self.other_user,
                'approver': self.user,
                'received_date': datetime.date.today(),
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_leader_step()
        res = self.client.get(self.url)
        self.assertContains(res, '<td class="columndocument_key"')

    def test_step_finished(self):
        doc = DocumentFactory(
            revision={
                'leader': self.other_user,
                'approver': self.user,
                'received_date': datetime.date.today(),
            }
        )
        doc.latest_revision.start_review()
        doc.latest_revision.end_review()
        res = self.client.get(self.url)
        self.assertNotContains(res, '<td class="columndocument_key"')


class ReviewFormTests(TestCase):

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
        self.url = reverse('review_document', args=['test_key'])

        self.filename = 'documents/tests/sample_doc_native.docx'

    def test_reviewers_submit_review_without_file(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()

        review = revision.get_review(self.user)
        self.assertEqual(review.status, 'progress')

        self.client.post(self.url, {'review': 'something'})
        review = revision.get_review(self.user)
        self.assertIsNotNone(review.closed_on)
        self.assertEqual(review.status, 'reviewed')
        self.assertFalse(review.comments)

    def test_reviewers_submit_review_with_file(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()

        with open(self.filename, 'rb') as fp:
            self.client.post(self.url, {'review': 'something', 'comments': fp})
            review = revision.get_review(self.user)
            self.assertTrue(review.comments)

    def test_all_reviewers_have_submitted_review(self):
        """When all reviewers have reviewed the doc, proceed to next step."""
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        self.assertIsNone(revision.reviewers_step_closed)

        self.client.post(self.url, {'review': 'something'})

        revision = revision.__class__.objects.get(pk=revision.pk)
        self.assertIsNotNone(revision.reviewers_step_closed)

    def test_non_reviewer_submit_review(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.other_user],
                'leader': self.user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        res = self.client.post(self.url, {'review': 'something'})
        self.assertEqual(res.status_code, 404)

    def test_reviewer_cannot_access_review_when_step_is_closed(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_reviewers_step()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

    def test_reviewer_cannot_do_the_same_review_twice(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()

        res = self.client.post(self.url, {'review': 'something'}, follow=True)
        self.assertEqual(res.status_code, 200)

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

        res = self.client.post(self.url, {'review': 'something'}, follow=True)
        self.assertEqual(res.status_code, 404)

    def test_leader_submit_review_without_file(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'leader': self.user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_reviewers_step()

        self.assertIsNone(revision.leader_step_closed)

        self.client.post(self.url, {'review': 'something'})
        revision = revision.__class__.objects.get(pk=revision.pk)
        self.assertIsNotNone(revision.leader_step_closed)

    def test_leader_submit_review_with_return_code(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'leader': self.user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_reviewers_step()

        self.client.post(self.url, {'review': 'something', 'return_code': '1'})
        review = revision.get_review(self.user, role='leader')
        self.assertEqual(review.return_code, '1')

        revision = doc.latest_revision
        self.assertEqual(revision.return_code, '1')

    def test_leader_submit_review_with_file(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'leader': self.user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_reviewers_step()

        with open(self.filename, 'rb') as fp:
            self.client.post(self.url, {'review': 'something', 'comments': fp})
            revision = revision.__class__.objects.get(pk=revision.pk)
            self.assertIsNotNone(revision.leader_step_closed)

    def test_leader_cannot_access_review_when_step_is_closed(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'leader': self.user,
                'approver': self.other_user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_leader_step()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

    def test_approver_submit_review_without_file(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'leader': self.other_user,
                'approver': self.user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_leader_step()

        self.assertIsNone(revision.review_end_date)

        self.client.post(self.url, {'review': 'something'})
        revision = revision.__class__.objects.get(pk=revision.pk)
        self.assertIsNotNone(revision.review_end_date)

    def test_approver_submit_review_with_file(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'leader': self.other_user,
                'approver': self.user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_leader_step()

        with open(self.filename, 'rb') as fp:
            self.client.post(self.url, {'review': 'something', 'comments': fp})
            revision = revision.__class__.objects.get(pk=revision.pk)
            self.assertIsNotNone(revision.review_end_date)

    def test_approver_cannot_access_a_closed_review(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'leader': self.other_user,
                'approver': self.user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_review()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

    def test_simple_reviewer_cannot_see_return_code_field(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.user],
                'leader': self.other_user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()

        res = self.client.get(self.url)
        self.assertNotContains(res, 'name="return_code"')

    def test_leader_can_see_return_code_field(self):
        doc = DocumentFactory(
            document_key='test_key',
            category=self.category,
            revision={
                'reviewers': [self.other_user],
                'leader': self.user,
                'received_date': datetime.date.today(),
            }
        )
        revision = doc.latest_revision
        revision.start_review()
        revision.end_reviewers_step()

        res = self.client.get(self.url)
        self.assertContains(res, 'name="return_code"')


class StartReviewTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category
        )
        self.doc = DocumentFactory(
            document_key='test_document',
            category=self.category,
            revision={
                'leader': self.user,
                'received_date': datetime.date.today(),
            }
        )
        self.client.login(email=self.user.email, password='pass')
        self.start_review_url = reverse('document_start_review', args=[
            self.category.organisation.slug,
            self.category.slug,
            'test_document'])

    def test_start_review_with_remarks(self):
        self.assertEqual(self.doc.note_set.all().count(), 0)

        res = self.client.post(
            self.start_review_url,
            {'body': 'This is a notification!'},
            follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.doc.note_set.all().count(), 1)

    def test_start_review_with_empty_remark(self):
        self.assertEqual(self.doc.note_set.all().count(), 0)

        res = self.client.post(
            self.start_review_url,
            {'body': ''},
            follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.doc.note_set.all().count(), 0)

    def test_start_review_with_no_remark(self):
        self.assertEqual(self.doc.note_set.all().count(), 0)

        res = self.client.post(self.start_review_url, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.doc.note_set.all().count(), 0)
