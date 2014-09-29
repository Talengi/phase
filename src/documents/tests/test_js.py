from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from selenium.webdriver.phantomjs.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from mock import patch

from accounts.factories import UserFactory
from categories.factories import CategoryFactory


class DocumentListTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(DocumentListTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(DocumentListTests, cls).tearDownClass()

    def setUp(self):
        self.category = CategoryFactory()
        user = UserFactory(email='testadmin@phase.fr', password='pass',
                           is_superuser=True,
                           category=self.category)
        document_list_url = reverse('category_document_list', args=[
            self.category.organisation.slug,
            self.category.slug
        ])
        self.url = '%s%s' % (self.live_server_url, document_list_url)

        # User login
        self.client.login(email=user.email, password='pass')
        cookie = self.client.cookies['sessionid']
        self.selenium.get(self.live_server_url + '/admin/')
        self.selenium.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.selenium.refresh()

    def test_initial_collection_fetch(self):
        self.selenium.get(self.url)
        rows = self.selenium.find_elements_by_css_selector('table#documents tbody tr')
        self.assertEqual(len(rows), 0)
        WebDriverWait(self.selenium, 2).until(
            lambda x: self.selenium.find_elements_by_css_selector('table#documents tbody tr'))

        rows = self.selenium.find_elements_by_css_selector('table#documents tbody tr')
        self.assertNotEqual(len(rows), 0)
