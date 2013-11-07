import tempfile

from django.test import TestCase

from documents.models import Document
from documents.management.commands import generate_documents
from categories.factories import CategoryFactory


class CommandTest(TestCase):

    def setUp(self):
        CategoryFactory()

    def test_generate_data(self):
        """
        Tests that you can generate documents with random values.
        """
        self.assertEqual(Document.objects.all().count(), 0)
        command = generate_documents.Command()
        command.stdout = tempfile.TemporaryFile()  # hackish.
        command.handle(2)
        self.assertEqual(Document.objects.all().count(), 2)
