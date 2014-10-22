# -*- coding: utf8 -*-
#
#            REINDEX
#                           ,,
#                          ';;
#                           ''
#             ____          ||
#            ;    \         ||
#             \,---'-,-,    ||
#             /     (  o)   ||
#           (o )__,--'-' \  ||
# ,,,,       ;'uuuuu''   ) ;;
# \   \      \ )      ) /\//
#  '--'       \'nnnnn' /  \
#    \\      //'------'    \
#     \\    //  \           \
#      \\  //    )           )
#       \\//     |           |
#        \\     /            |
#
#           ALL THE THINGS !!!

from __future__ import unicode_literals

import logging
import datetime

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection

from categories.models import Category
from search.utils import index_document

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_reindex = datetime.datetime.now()
        logger.info('Reindex starting at %s' % start_reindex)

        call_command('delete_index', **options)
        call_command('create_index', **options)
        call_command('set_mappings', **options)

        categories = Category.objects \
            .select_related(
                'organisation',
                'category_template',
                'category_template__metadata_model'
            )

        for category in categories:
            document_type = category.document_type()
            DocumentClass = category.category_template.metadata_model.model_class()
            documents = DocumentClass.objects \
                .select_related(
                    'latest_revision',
                    'latest_revision__leader',
                    'latest_revision__approver',
                    'document',
                    'document__category',
                    'document__category__category_template',
                    'document__category__organisation') \
                .filter(document__category=category)

            for metadata in documents:
                document = metadata.document
                index_document.delay(document.id, document_type, metadata.jsonified())

        end_reindex = datetime.datetime.now()
        logger.info('Reindex ending at %s' % end_reindex)
