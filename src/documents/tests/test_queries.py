from django.test import TestCase
from django.core.urlresolvers import reverse
from django.db import connections, DEFAULT_DB_ALIAS, reset_queries
from django.core.signals import request_started

from accounts.factories import UserFactory
from documents.factories import DocumentFactory, RevisionFactory


class AssertMaxQueriesContext(object):
    def __init__(self, test_case, num, connection):
        self.test_case = test_case
        self.num = num
        self.connection = connection

    def __enter__(self):
        self.old_debug_cursor = self.connection.use_debug_cursor
        self.connection.use_debug_cursor = True
        self.starting_queries = len(self.connection.queries)
        request_started.disconnect(reset_queries)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.use_debug_cursor = self.old_debug_cursor
        request_started.connect(reset_queries)
        if exc_type is not None:
            return

        final_queries = len(self.connection.queries)
        executed = final_queries - self.starting_queries

        self.test_case.assertTrue(
            executed <= self.num, "%d queries executed, less than %d expected" % (
                executed, self.num
            )
        )


class QueriesTest(TestCase):
    """Test that main pages generate less than 5 queries.

    In the DoD: A page must be limited at 5 queries.

    """
    fixtures = ['initial_data.json']

    def assertMaxQueries(self, num, func=None, *args, **kwargs):
        using = kwargs.pop("using", DEFAULT_DB_ALIAS)
        conn = connections[using]

        context = AssertMaxQueriesContext(self, num, conn)
        if func is None:
            return context

        with context:
            func(*args, **kwargs)

    def setUp(self):
        # Login as admin by default so we won't be bothered by missing permissions
        user = UserFactory(email='testadmin@phase.fr', password='pass',
                           is_superuser=True)
        self.client.login(email=user.email, password='pass')

    def test_document_list(self):
        url = reverse('document_list')
        with self.assertMaxQueries(5):
            self.client.get(url)

    def test_document_detail(self):
        document = DocumentFactory()
        RevisionFactory(document=document)
        url = reverse('document_detail', args=[document.document_number])

        with self.assertMaxQueries(5):
            self.client.get(url)
