# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<contractor_id>'
    help = 'Import existing transmittals for a given contractor.'

    def handle(self, *args, **options):
        print args
