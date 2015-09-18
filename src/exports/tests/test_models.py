# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from uuid import UUID

from django.test import TestCase
from django.utils.timezone import UTC

from categories.factories import CategoryFactory
from accounts.factories import UserFactory
from exports.factories import ExportFactory
from exports.generators import ExportGenerator
from exports.formatters import CSVFormatter


class ExportTests(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)

    def create_export(self, **kwargs):
        data = {
            'owner': self.user,
            'category': self.category}
        data.update(kwargs)
        return ExportFactory(**data)

    def test_get_filename(self):
        uuid = UUID('12345678-1234-5678-1234-567812345678')
        date = datetime.datetime(2015, 1, 1, tzinfo=UTC())
        export = self.create_export(id=uuid, created_on=date)

        filename = export.get_filename()
        self.assertEqual(
            filename,
            'export_20150101_12345678-1234-5678-1234-567812345678.csv')

    def test_get_data_generator(self):
        export = self.create_export()
        generator = export.get_data_generator()
        self.assertTrue(isinstance(generator, ExportGenerator))

    def test_get_data_formatter(self):
        export = self.create_export()
        formatter = export.get_data_formatter()
        self.assertTrue(isinstance(formatter, CSVFormatter))

    def test_get_filters(self):
        qs = 'toto=riri&tata=fifi&tutu=loulou'
        export = self.create_export(querystring=qs)
        filters = export.get_filters()
        self.assertEqual(filters['toto'], 'riri')
        self.assertEqual(filters['tata'], 'fifi')
        self.assertEqual(filters['tutu'], 'loulou')
