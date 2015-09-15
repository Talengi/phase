# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import CreateView

from exports.models import Export


class ExportCreate(CreateView):
    model = Export
