import os.path

from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from casper.tests import CasperTestCase

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from bookmarks.factories import BookmarkFactory
from search.signals import connect_signals, disconnect_signals
from search.utils import create_index, delete_index, put_category_mapping


@override_settings(PAGINATE_BY=5)
class DocumentListTests(CasperTestCase):
    no_colors = False

    def setUp(self):
        delete_index()
        create_index()

        self.category = CategoryFactory()
        self.slug = '/{}/{}/'.format(
            self.category.organisation.slug,
            self.category.category_template.slug)
        put_category_mapping(self.category.id)
        user = UserFactory(email='testadmin@phase.fr', password='pass',
                           is_superuser=True,
                           category=self.category)

        connect_signals()
        for doc_id in range(20):
            DocumentFactory(
                document_key='hazop-report-%d' % doc_id,
                category=self.category,
            )

        document_list_url = reverse('category_document_list', args=[
            self.category.organisation.slug,
            self.category.slug
        ])

        self.b1 = BookmarkFactory(
            user=user,
            category=self.category,
            name='Hazop documents',
            url='%s?search_terms=hazop' % document_list_url
        )
        self.b2 = BookmarkFactory(
            user=user,
            category=self.category,
            name='Rev ordered documents',
            url='%s?sort_by=current_revision' % document_list_url
        )

        self.url = '%s%s' % (self.live_server_url, document_list_url)
        self.client.login(email=user.email, password='pass')
        self.test_file = os.path.join(
            os.path.dirname(__file__),
            'casper_tests',
            'tests.js'
        )

    def tearDown(self):
        disconnect_signals()
        delete_index()

    def test_js(self):
        self.assertTrue(self.casper(
            self.test_file,
            url=self.url,
            slug=self.slug,
            b1_id=self.b1.id,
            b2_id=self.b2.id,
        ))
