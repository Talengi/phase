# -*- coding: utf8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.test.utils import override_settings

from mock import patch

from categories.factories import CategoryFactory
from search.signals import connect_signals


@override_settings(ELASTIC_AUTOINDEX=True)
class SignalTests(TestCase):
    def setUp(self):
        connect_signals()

    @patch('search.signals.put_category_mapping.delay')
    def test_new_category_mapping_are_created(self, index_mock):
        CategoryFactory()
        self.assertEqual(index_mock.call_count, 1)
