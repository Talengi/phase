# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import factory

from exports.models import Export


class ExportFactory(factory.DjangoModelFactory):
    class Meta:
        model = Export

    querystring = ''
