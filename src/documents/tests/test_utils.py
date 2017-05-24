from datetime import date

from django.test import TestCase

from documents.utils import stringify_value


class UtilsTest(TestCase):

    def test_stringify_value(self):
        self.assertEqual('toto', stringify_value('toto'))
        self.assertEqual('2042-12-01', stringify_value(date(2042, 12, 1)))
        self.assertEqual('Yes', stringify_value(True))
        self.assertEqual('No', stringify_value(False))
        self.assertEqual('NC', stringify_value(None))
