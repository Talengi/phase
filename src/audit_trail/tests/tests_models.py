from django.test import TestCase

from ..factories import ActivityFactory


class ActivityTests(TestCase):
    def test_activity_model(self):
        activity = ActivityFactory()
        self.assertTrue(activity.verb)
