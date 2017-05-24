# -*- coding: utf-8 -*-


import factory

from exports.models import Export


class ExportFactory(factory.DjangoModelFactory):
    class Meta:
        model = Export

    querystring = ''
