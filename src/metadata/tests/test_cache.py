# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.forms.models import modelform_factory

from metadata.models import ValuesList
from metadata.factories import ValuesListFactory, ListEntryFactory
from metadata.fields import get_choices_from_list
from metadata.handlers import populate_values_list_cache
from metadata.admin import ValuesListAdmin


class MockRequest(object):
    pass


class MockSuperUser(object):
    def has_perm(self, perm):
        return True

request = MockRequest()
request.user = MockSuperUser()


ValuesListForm = modelform_factory(ValuesList, fields=('index', 'name'))


class AdminCacheTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ValuesListAdmin(ValuesList, self.site)
        self.values_list = ValuesListFactory(
            values={
                'test1': 'Test 1',
                'test2': 'Test 2',
                'test3': 'Test 3',
            }
        )
        populate_values_list_cache()

    def test_cache_is_updated_when_form_is_saved(self):
        self.values_list.values.add(ListEntryFactory(
            index='test4',
            value='Test 4'))
        choices = get_choices_from_list(self.values_list.index)
        self.assertItemsEqual(choices, [
            (u'test1', u'test1 - Test 1'),
            (u'test2', u'test2 - Test 2'),
            (u'test3', u'test3 - Test 3'),
        ])

        form = ValuesListForm(instance=self.values_list)
        self.admin.save_model(request, self.values_list, form, True)

        choices = get_choices_from_list(self.values_list.index)
        self.assertItemsEqual(choices, [
            (u'test1', u'test1 - Test 1'),
            (u'test2', u'test2 - Test 2'),
            (u'test3', u'test3 - Test 3'),
            (u'test4', u'test4 - Test 4'),
        ])
