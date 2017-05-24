from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.factories import UserFactory
from ..models import Activity
from ..signals import activity_log
from documents.factories import DocumentFactory


class ActivityApiTests(TestCase):

    def setUp(self):
        super(ActivityApiTests, self).setUp()
        self.apiclient = APIClient()
        self.user = UserFactory(
            email='testadmin@phase.fr', password='pass', is_superuser=True)
        self.apiclient.login(email=self.user.email, password='pass')

    def test_view(self):
        doc = DocumentFactory()
        doc.category.users.add(self.user)

        activity_log.send(verb=Activity.VERB_CREATED,
                          target=doc,
                          sender=None,
                          actor=self.user)
        activity_log.send(verb=Activity.VERB_EDITED,
                          target=None,
                          action_object=doc,
                          sender=None,
                          actor=self.user)
        url = reverse(
            'document_audit_trail',
            args=[doc.category.organisation.slug,
                  doc.category.slug,
                  doc.document_key])
        res = self.apiclient.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 2)
