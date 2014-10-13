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

from django.core.management.base import BaseCommand
from django.core.management import call_command

from documents.models import Document
from search.utils import index_document


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('delete_index', **options)
        call_command('create_index', **options)
        call_command('set_mappings', **options)

        # This method is highly inefficient, since we are making way too
        # much sql queries and http requests.
        # We don't really care, however, since this command should only
        # be used exceptionnaly (e.g post syncdb)
        docs = Document.objects.all()
        for doc in docs:
            index_document.delay(doc.id, doc.document_type(), doc.to_json())
