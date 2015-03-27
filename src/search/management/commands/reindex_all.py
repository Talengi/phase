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
import sys
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils.six.moves import input

from categories.models import Category
from search.utils import index_document

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--noinput',
            action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
    )

    def handle(self, *args, **options):
        interactive = options.get('interactive')
        if interactive:
            confirm = input("""
You have requested a flush of the search index.
This will IRREVERSIBLY DESTROY all data currently indexed by Elasticsearch.
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: """)
        else:
            confirm = 'yes'

        if confirm != 'yes':
            sys.exit(1)

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
                .select_related() \
                .filter(document__category=category)

            for metadata in documents:
                document = metadata.document
                if document.is_indexable:
                    index_document.delay(document.id, document_type, metadata.jsonified())

        end_reindex = datetime.datetime.now()
        logger.info('Reindex ending at %s' % end_reindex)
