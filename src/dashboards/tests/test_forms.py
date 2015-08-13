# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.forms.models import modelform_factory

from categories.factories import CategoryFactory
from dashboards.models import Dashboard
from dashboards.dashboards import EmptyDashboard


class IAmNotADashboardProvider(object):
    pass


DashboardForm = modelform_factory(Dashboard, fields=('data_provider',))


class DashboardFieldTests(TestCase):

    def setUp(self):
        self.category = CategoryFactory()

    def test_provider_is_of_wrong_type(self):
        with self.assertRaises(ValidationError):
            dashboard = Dashboard(
                category=self.category,
                data_provider=IAmNotADashboardProvider)
            dashboard.full_clean()

    def test_provider_class_does_not_exist(self):
        with self.assertRaises(ValidationError):
            dashboard = Dashboard(
                category=self.category,
                data_provider='i.do.not.exist')
            dashboard.full_clean()

    def test_form_field_values(self):
        form = DashboardForm()
        choices = dict(form.fields['data_provider'].choices).keys()
        self.assertTrue(EmptyDashboard in choices)

    def test_form_widget_values(self):
        form = DashboardForm()
        choices = dict(form.fields['data_provider'].widget.choices).keys()
        self.assertTrue('dashboards.dashboards.EmptyDashboard' in choices)

    def test_correct_option_is_selected(self):
        dashboard = Dashboard(
            category=self.category,
            data_provider=EmptyDashboard)
        form = DashboardForm(instance=dashboard)
        widget = form['data_provider'].as_widget()
        selected_option = 'option value="dashboards.dashboards.EmptyDashboard" selected="selected'
        self.assertTrue(selected_option in widget)

    def test_settings_field_sets_data_on_instance(self):
        data = {
            'data_provider': 'dashboards.dashboards.EmptyDashboard'}
        form = DashboardForm(data)
        dashboard = form.save(commit=False)
        self.assertEqual(dashboard.data_provider, EmptyDashboard)
