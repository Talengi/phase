import factory

from .models import Organisation, CategoryTemplate, Category


class OrganisationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Organisation

    name = factory.Sequence(lambda n: 'Organisation {0}'.format(n))
    slug = factory.Sequence(lambda n: 'organisation_{0}'.format(n))


class CategoryTemplateFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CategoryTemplate

    name = factory.Sequence(lambda n: 'Category {0}'.format(n))
    slug = factory.Sequence(lambda n: 'category_{0}'.format(n))
    description = 'Test category'


class CategoryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Category

    organisation = factory.SubFactory(OrganisationFactory)
    category_template = factory.SubFactory(CategoryTemplateFactory)
