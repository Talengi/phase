# -*- coding: utf-8 -*-


import os.path
import time

from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from casper.tests import CasperTestCase

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from search.signals import connect_signals, disconnect_signals
from search.utils import (create_index, delete_index, put_category_mapping,
                          index_document)


@override_settings(PAGINATE_BY=5)
class DocumentListTests(CasperTestCase):

    def setUp(self):
        delete_index()
        create_index()

        self.category = CategoryFactory()
        put_category_mapping(self.category.id)
        user = UserFactory(email='testadmin@phase.fr', password='pass',
                           is_superuser=True,
                           category=self.category)

        connect_signals()
        for doc_id in range(20):
            doc = DocumentFactory(
                document_key='hazop-report-%d' % doc_id,
                category=self.category,
            )
            index_document(doc.id)

        # ES needs some time to finish indexing
        time.sleep(1)

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
        disconnect_signals()
        delete_index()

    def test_js(self):
        self.assertTrue(self.casper(
            self.test_file,
            url=self.url
        ))
