from django.core.urlresolvers import reverse
from django.test import TestCase

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory


class CategoryBreadcrumbTest(TestCase):
    """Test that the mini category breadcrumb is displayed correctly in headbar."""

    def setUp(self):
        self.category = CategoryFactory()
        self.document = DocumentFactory(
            document_key='hazop-report',
            category=self.category,
        )
        user = UserFactory(email='testadmin@phase.fr', password='pass',
                           is_superuser=True,
                           category=self.category)
        self.client.login(email=user.email, password='pass')
        self.html = '''
        <p class="category-info navbar-text hidden-xs hidden-sm">
            <span class="glyphicon glyphicon-info-sign"></span>
            %s &gt; %s
        </p>
        ''' % (self.category.organisation.name, self.category.name)

    def test_document_list(self):
        url = self.category.get_absolute_url()
        res = self.client.get(url)
        self.assertContains(res, self.html, html=True)

    def test_document_detail(self):
        url = self.document.get_absolute_url()
        res = self.client.get(url)
        self.assertContains(res, self.html, html=True)

    def test_home(self):
        url = reverse('category_list')
        res = self.client.get(url)
        self.assertNotContains(res, self.html, html=True)
