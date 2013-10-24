import datetime
import factory
from factory.fuzzy import FuzzyDate

from .models import Document, DocumentRevision, Category


fuzzy_date = FuzzyDate(datetime.date(2012, 1, 1))


class DocumentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Document

    title = factory.Sequence(lambda n: 'Document {0}'.format(n))
    sequencial_number = factory.Sequence(lambda n: '{0}'.format(n))
    current_revision_date = fuzzy_date.fuzz()
    current_revision = '00'


class RevisionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DocumentRevision

    revision = factory.Sequence(lambda n: '{0}'.format(n))
    revision_date = fuzzy_date.fuzz()
    factory.SubFactory(DocumentFactory)


class CategoryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Category

    name = factory.Sequence(lambda n: 'Category {0}'.format(n))
    description = 'Test category'
