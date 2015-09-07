# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from metadata.factories import ValuesListFactory
from metadata.fields import get_choices_from_list
from metadata.handlers import populate_values_list_cache


class ConfigurableChoiceFieldTest(TestCase):
    def setUp(self):
        self.values_list = ValuesListFactory(
            values={
                'test1': 'Test 1',
                'test2': 'Test 2',
                'test3': 'Test 3',
            }
        )
        populate_values_list_cache()

    def test_choices_from_list(self):
        choices = get_choices_from_list(self.values_list.index)
        self.assertItemsEqual(choices, [
            (u'test1', u'test1 - Test 1'),
            (u'test2', u'test2 - Test 2'),
            (u'test3', u'test3 - Test 3'),
        ])
