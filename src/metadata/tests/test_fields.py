from django.test import TestCase

from metadata.factories import ValuesListFactory
from metadata.fields import get_choices_from_list


class ConfigurableChoiceFieldTest(TestCase):
    def test_choices_from_list(self):
        values_list = ValuesListFactory(
            values={
                'test1': 'Test 1',
                'test2': 'Test 2',
                'test3': 'Test 3',
            }
        )
        choices = get_choices_from_list(values_list.index)
        self.assertItemsEqual(choices, [
            (u'test1', u'Test 1'),
            (u'test2', u'Test 2'),
            (u'test3', u'Test 3'),
        ])
