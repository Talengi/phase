from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.factories import UserFactory
from categories.factories import CategoryFactory


class ReportTest(TestCase):
    def setUp(self):
        self.category = CategoryFactory()
        self.user = UserFactory(
            name='User',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(username=self.user.email, password='pass')

    def test_report_page_with_disabled_display_reporting(self):
        url = reverse('category_report', args=[
            self.category.organisation.slug,
            self.category.slug
        ])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)

    def test_report_page(self):
        category_template = self.category.category_template
        category_template.display_reporting = True
        category_template.save()
        url = reverse('category_report', args=[
            self.category.organisation.slug,
            self.category.slug
        ])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.context['reporting_active'])
