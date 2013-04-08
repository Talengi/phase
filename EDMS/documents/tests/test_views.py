from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse


class DocumentListTest(TestCase):
    fixtures = ['initial_data.json']

    def test_document_number(self):
        """
        Tests that a document list view returns all documents.
        """
        c = Client()
        r = c.get(reverse("document_list"))
        self.assertEqual(len(r.context['document_list']), 500)
