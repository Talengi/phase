import factory

from .models import DummyMetadata, DummyMetadataRevision


class MetadataFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DummyMetadata


class MetadataRevisionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DummyMetadataRevision
