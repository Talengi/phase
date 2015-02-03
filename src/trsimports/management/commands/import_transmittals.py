# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<contractor_id>'
    help = 'Import existing transmittals for a given contractor.'

    def handle(self, *args, **options):
        if len(args) != 1:
            error = 'You must provide a contractor id as an argument'
            raise CommandError(error)

        contractor_id = args[0]

        path_config = settings.TRS_IMPORTS_PATHS
        ctr_path_config = path_config.get(contractor_id, None)
        if ctr_path_config is None:
            raise ImproperlyConfigured('The "%s" contractor is unknown. '
                                       'Check your configuration' % contractor_id)
