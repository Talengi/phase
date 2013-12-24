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
    def _prepare(cls, create, **kwargs):
        if not 'metadata' in kwargs:
            kwargs.update({
                'metadata': ContentType.objects.get_for_model(DemoMetadata)
            })
        return super(DocumentFactory, cls)._prepare(create, **kwargs)

    @classmethod
    def _after_postgeneration(cls, obj, create, results=None):
        revision = MetadataRevisionFactory(
            document=obj,
            revision=obj.current_revision,
            revision_date=obj.current_revision_date)

        obj.metadata = MetadataFactory(
            document=obj,
            document_key=obj.document_key,
            latest_revision=revision)

        if create and results:
            obj.save()
