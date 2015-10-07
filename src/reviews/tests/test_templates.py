# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from accounts.factories import UserFactory


class ReviewableDocumentDetail(TestCase):

    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(username=self.user.email, password='pass')

        self.doc = DocumentFactory(
            category=self.category,
            revision={
                'leader': self.user,
                'received_date': timezone.now(),
            }
        )
        self.url = reverse("document_detail", args=[
            self.category.organisation.slug,
            self.category.slug,
            self.doc.document_key
        ])

    def test_user_can_update_review(self):
        self.doc.latest_revision.start_review()
        res = self.client.get(self.url)
        self.assertNotContains(res, 'Modify your comment')

        review = self.doc.latest_revision.get_review(self.user)
        review.post_review(comments=None)

        res = self.client.get(self.url)
        self.assertContains(res, 'Modify your comment')
