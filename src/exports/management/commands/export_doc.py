# -*- coding: utf-8 -*-


import logging

from django.core.management.base import BaseCommand, CommandError

from exports.models import Export
from documents.models import Document
from accounts.models import User


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Manually create a single document export."""

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('document_key', type=str)
        parser.add_argument('format', type=str)

    def handle(self, *args, **options):
        # Extract user
        username = options['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError('This user does not exist.')

        # Extract document
        doc_key = options['document_key']
        try:
            document = Document.objects.get(document_key=doc_key)
        except Document.DoesNotExist:
            raise CommandError('This document does not exist.')
        querystring = 'document_key={}'.format(doc_key)

        fmt = options['format']

        self.stdout.write('Starting export')
        export = Export.objects.create(
            owner=user,
            category=document.category,
            querystring=querystring,
            format=fmt,
            status=Export.STATUSES.processing)

        msg = 'Exporting to {}'.format(export.get_filepath())
        self.stdout.write(msg)

        try:
            export.write_file()
            export.status = Export.STATUSES.done
            export.save()
        except:  # noqa
            self.stderr.write('Error writing file, cleaning stalled export.')
            export.delete()
            raise
