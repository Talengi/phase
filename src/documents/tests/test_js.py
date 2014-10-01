import os.path

from django.core.urlresolvers import reverse
from casper.tests import CasperTestCase

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from search.utils import index_document, unindex_document


class DocumentListTests(CasperTestCase):

    def setUp(self):
        self.category = CategoryFactory()
        user = UserFactory(email='testadmin@phase.fr', password='pass',
                           is_superuser=True,
                           category=self.category)
        self.document = DocumentFactory(
            document_key='hazop-report',
            category=self.category,
        )
        index_document(self.document)
        document_list_url = reverse('category_document_list', args=[
            self.category.organisation.slug,
            self.category.slug
        ])
        self.url = '%s%s' % (self.live_server_url, document_list_url)
        self.client.login(email=user.email, password='pass')
        self.test_file = os.path.join(
            os.path.dirname(__file__),
            'casper_tests',
            'tests.js'
        )

    def tearDown(self):
        unindex_document(self.document)

    def test_js(self):
        self.assertTrue(self.casper(
            self.test_file,
            url=self.url
        ))
