import factory

from .models import DemoMetadata, DemoMetadataRevision


class MetadataFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DemoMetadata
    title = factory.Sequence(lambda n: 'Title {0}'.format(n))



class MetadataRevisionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DemoMetadataRevision
