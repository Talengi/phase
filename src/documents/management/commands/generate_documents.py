#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from documents.tests.utils import generate_random_documents


class Command(BaseCommand):
    args = '<number_of_documents>'
    help = 'Creates a given number of random documents'

    def handle(self, *args, **options):
        nb_of_docs = int(args[0])
        generate_random_documents(nb_of_docs)

        self.stdout.write(
            'Successfully generated {nb_of_docs} documents'.format(
                nb_of_docs=nb_of_docs,
            )
        )
