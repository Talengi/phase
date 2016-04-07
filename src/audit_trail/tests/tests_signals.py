from django.test import TestCase

from accounts.factories import UserFactory
from documents.factories import DocumentFactory

from ..models import Activity
from ..signals import activity_log


class ActivitySignalTests(TestCase):
    def test_signal(self):
        doc = DocumentFactory()
        user = UserFactory()
        self.assertEqual(Activity.objects.count(), 0)
        activity_log.send(verb=Activity.VERB_EDITED, target=doc, sender='self', actor=user)

        latest_activity = Activity.objects.all().get()
        self.assertEqual(latest_activity.verb, 'edited')
        self.assertEqual(latest_activity.actor, user)
        self.assertEqual(latest_activity.actor_object_str, str(user))
        self.assertEqual(latest_activity.target, doc)
        self.assertEqual(latest_activity.target_object_str, str(doc))
