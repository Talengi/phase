import os.path

from django.core.urlresolvers import reverse
from casper.tests import CasperTestCase

from accounts.factories import UserFactory
from categories.factories import CategoryFactory
from documents.factories import DocumentFactory
from discussion.factories import NoteFactory


class DocumentListTests(CasperTestCase):

    def setUp(self):
        self.category = CategoryFactory()
        user = UserFactory(
            email='testadmin@phase.fr',
            password='pass',
            is_superuser=True,
            category=self.category)
        self.client.login(email=user.email, password='pass')

        user2 = UserFactory(email='otheruser@phase.fr', category=self.category)

        doc = DocumentFactory(
            document_key='hazop-report-1',
            category=self.category,
            revision={
                'leader': user,
            }

        )
        doc.latest_revision.start_review()

        for _ in xrange(5):
            for u in (user, user2):
                NoteFactory(
                    author=u,
                    document=doc,
                    revision=1)

        review_url = reverse('review_document', args=[doc.document_key])
        self.url = '%s%s' % (self.live_server_url, review_url)
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
