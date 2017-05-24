#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from documents.tests.utils import generate_random_documents
from categories.models import Category


class Command(BaseCommand):
    args = '<number_of_documents> <category_id>'
    help = 'Creates a given number of random documents'

    def handle(self, *args, **options):
        nb_of_docs = int(args[0])
        category_id = int(args[1])

        category = Category.objects.get(pk=category_id)

        generate_random_documents(nb_of_docs, category)

        self.stdout.write(
            'Successfully generated {nb_of_docs} documents'.format(
                nb_of_docs=nb_of_docs,
            ).encode()
        )
