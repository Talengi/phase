import datetime

from django.contrib.contenttypes.models import ContentType
import factory
from factory.fuzzy import FuzzyDate

from .models import Document
from document_types.models import ContractorDeliverable


fuzzy_date = FuzzyDate(datetime.date(2012, 1, 1))


class DocumentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Document

    document_key = factory.Sequence(lambda n: 'document-{0}'.format(n))
    current_revision_date = fuzzy_date.fuzz()
    current_revision = 1

    @classmethod
    def _prepare(cls, create, **kwargs):
        if not 'metadata' in kwargs:
            kwargs.update({
                'metadata': ContentType.objects.get_for_model(ContractorDeliverable)
            })
        return super(DocumentFactory, cls)._prepare(create, **kwargs)
#class RevisionFactory(factory.DjangoModelFactory):
#    FACTORY_FOR = DocumentRevision
#
#    revision = factory.Sequence(lambda n: '{0}'.format(n))
#    revision_date = fuzzy_date.fuzz()
#    document = factory.SubFactory(DocumentFactory)
