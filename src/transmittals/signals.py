# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.dispatch import Signal


related_documents_saved = Signal(providing_args=['instance'])
