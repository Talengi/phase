from django.test import TestCase
from django.core.urlresolvers import reverse

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory


delete_button = '<a id="action-delete-document"'


class DocumentDetailTests(TestCase):
    """Test action menu items"""
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

    def test_admin_can_delete_document(self):
        res = self.client.get(self.url)
        self.assertContains(res, delete_button)

    def test_simple_user_cannot_delete_document(self):
        self.user.is_superuser = False
        self.user.save()

        res = self.client.get(self.url)
        self.assertNotContains(res, delete_button)
