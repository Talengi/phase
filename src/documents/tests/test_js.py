import os.path

from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from casper.tests import CasperTestCase

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from search.utils import index_document


@override_settings(PAGINATE_BY=5)
class DocumentListTests(CasperTestCase):

    def setUp(self):
        self.category = CategoryFactory()
        user = UserFactory(email='testadmin@phase.fr', password='pass',
                           is_superuser=True,
                           category=self.category)

        for doc_id in xrange(20):
            document = DocumentFactory(
                document_key='hazop-report-%d' % doc_id,
                category=self.category,
            )
            index_document(document)

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

    def test_js(self):
        self.assertTrue(self.casper(
            self.test_file,
            url=self.url
        ))
