from django.test import TestCase

from transmittals.models import OutgoingTransmittal
from ..factories import CategoryFactory, CategoryTemplateFactory
from django.contrib.contenttypes.models import ContentType


class CategoryFactoryTests(TestCase):
    """Test CategoryFactory."""

    def test_category_factory(self):
        """Default generation."""
        category = CategoryFactory()
        assert category.pk
        assert category.category_template.pk
        assert category.category_template.metadata_model.pk


class CategoryTemplateFactoryTests(TestCase):
    """Test CategoryTemplateFactory with differents configurations."""

    def test_category_template_model_factory(self):
        """Default generation."""
        tpl = CategoryTemplateFactory()
        assert tpl.pk
        assert tpl.metadata_model.pk  # metadata_model is created

    def test_category_with_metadata_model_factory(self):
        """Providing a given content type."""
        ct = ContentType.objects.get_for_model(OutgoingTransmittal)
        tpl = CategoryTemplateFactory(metadata_model=ct)
        assert tpl.pk
        assert tpl.metadata_model == ct
