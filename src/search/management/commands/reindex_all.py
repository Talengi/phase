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



import logging
import datetime
import sys

from elasticsearch.helpers import bulk

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils.six.moves import input

from documents.utils import get_all_revision_classes
from search import elastic
from search.utils import build_index_data
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            '--noinput',
            action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.')

    def handle(self, *args, **options):
        interactive = options.get('interactive')
        if interactive:
            confirm = eval(input("""
You have requested a flush of the search index.
This will IRREVERSIBLY DESTROY all data currently indexed by Elasticsearch.
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: """))
        else:
            confirm = 'yes'

        if confirm != 'yes':
            sys.exit(1)

        start_reindex = datetime.datetime.now()
        logger.info('Reindex starting at %s' % start_reindex)

        call_command('delete_index', **options)
        call_command('create_index', **options)
        call_command('set_mappings', **options)

        logger.info('Preparing index data')

        classes = get_all_revision_classes()
        for class_ in classes:
            revisions = class_.objects \
                .filter(metadata__document__is_indexable=True) \
                .select_related()

            actions = []
            logger.info('Starting gathering data for documents of type {}'.format(class_.__name__))
            for revision in revisions:
                actions.append(build_index_data(revision))

            bulk(
                elastic,
                actions,
                chunk_size=settings.ELASTIC_BULK_SIZE,
                request_timeout=600)

        end_reindex = datetime.datetime.now()
        logger.info('Reindex ending at %s' % end_reindex)
