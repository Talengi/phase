# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import factory
from django.contrib.contenttypes.models import ContentType

from default_documents.models import DemoMetadata
from .models import Organisation, CategoryTemplate, Category


class OrganisationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Organisation

    name = factory.Sequence(lambda n: 'Organisation {0}'.format(n))
    slug = factory.Sequence(lambda n: 'organisation_{0}'.format(n))
    trigram = factory.fuzzy.FuzzyText(length=3)


class CategoryTemplateFactory(factory.DjangoModelFactory):
    class Meta:
        model = CategoryTemplate

    name = factory.Sequence(lambda n: 'Category {0}'.format(n))
    slug = factory.Sequence(lambda n: 'category_{0}'.format(n))
    description = 'Test category'

    @classmethod
    def _prepare(cls, create, **kwargs):
        if 'metadata_model' not in kwargs:
            kwargs.update({
                'metadata_model': ContentType.objects.get_for_model(DemoMetadata)
            })
        return super(CategoryTemplateFactory, cls)._prepare(create, **kwargs)


class CategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Category

    organisation = factory.SubFactory(OrganisationFactory)
    category_template = factory.SubFactory(CategoryTemplateFactory)
