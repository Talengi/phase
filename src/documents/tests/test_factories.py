from django.test import TestCase

from ..factories import DocumentFactory


class DocumentFactoryTests(TestCase):
    """Test DocumentFactory."""

    def test_document_factory(self):
        """Default generation."""
        doc = DocumentFactory()
        assert doc.pk
