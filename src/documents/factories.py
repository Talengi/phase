import datetime

from django.contrib.contenttypes.models import ContentType
import factory
from factory.fuzzy import FuzzyDate

from document_types.models import DemoMetadata
from document_types.factories import MetadataFactory, MetadataRevisionFactory
from categories.factories import CategoryFactory
from .models import Document


fuzzy_date = FuzzyDate(datetime.date(2012, 1, 1))


class DocumentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Document

    document_key = factory.Sequence(lambda n: 'document-{0}'.format(n))
    current_revision = 1
    current_revision_date = fuzzy_date.fuzz()
    category = factory.SubFactory(CategoryFactory)

    @classmethod
    def create(cls, **kwargs):
        """Takes custom args to set metadata and revision fields."""
        cls.metadata_kwargs = kwargs.pop('metadata', {})
        cls.revision_kwargs = kwargs.pop('revision', {})
        return super(DocumentFactory, cls).create(**kwargs)

    @classmethod
    def _prepare(cls, create, **kwargs):
        if not 'metadata' in kwargs:
            kwargs.update({
                'metadata': ContentType.objects.get_for_model(DemoMetadata)
            })
        return super(DocumentFactory, cls)._prepare(create, **kwargs)

    @classmethod
    def _after_postgeneration(cls, obj, create, results=None):
        revision_kwargs = {
            'document': obj,
            'revision': obj.current_revision,
            'revision_date': obj.current_revision_date,
            'created_on': obj.current_revision_date,
            'updated_on': obj.current_revision_date,
        }
        revision_kwargs.update(cls.revision_kwargs)
        revision = MetadataRevisionFactory(**revision_kwargs)

        metadata_kwargs = {
            'document': obj,
            'document_key': obj.document_key,
            'latest_revision': revision
        }
        metadata_kwargs.update(cls.metadata_kwargs)
        obj.metadata = MetadataFactory(**metadata_kwargs)

        if create and results:
            obj.save()
