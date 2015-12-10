import datetime

import factory
from factory.fuzzy import FuzzyDate

from default_documents.factories import MetadataFactory, MetadataRevisionFactory
from categories.factories import CategoryFactory
from .models import Document


fuzzy_date = FuzzyDate(datetime.date(2012, 1, 1))


class DocumentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Document

    document_key = factory.Sequence(lambda n: 'document-{0}'.format(n))
    document_number = factory.SelfAttribute('document_key')
    current_revision = 1
    current_revision_date = fuzzy_date.fuzz()
    category = factory.SubFactory(CategoryFactory)

    @classmethod
    def create(cls, **kwargs):
        """Takes custom args to set metadata and revision fields."""
        cls.metadata_factory_class = kwargs.pop('metadata_factory_class', MetadataFactory)
        cls.metadata_kwargs = kwargs.pop('metadata', {})

        cls.revision_factory_class = kwargs.pop('revision_factory_class', MetadataRevisionFactory)
        cls.revision_kwargs = kwargs.pop('revision', {})
        return super(DocumentFactory, cls).create(**kwargs)

    @classmethod
    def _after_postgeneration(cls, obj, create, results=None):
        revision_kwargs = {
            'document': obj,
            'revision': obj.current_revision,
            'revision_date': obj.current_revision_date,
            'received_date': obj.current_revision_date,
            'created_on': obj.current_revision_date,
            'updated_on': obj.current_revision_date,
        }
        revision_kwargs.update(cls.revision_kwargs)
        revision = cls.revision_factory_class(**revision_kwargs)

        metadata_kwargs = {
            'document': obj,
            'document_key': obj.document_key,
            'document_number': obj.document_number,
            'latest_revision': revision
        }
        metadata_kwargs.update(cls.metadata_kwargs)
        cls.metadata_factory_class(**metadata_kwargs)

        if create and results:
            obj.save()
