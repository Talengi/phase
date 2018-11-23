from django.test import TestCase

from ..factories import ValuesListFactory


class ValuesListFactoryTests(TestCase):
    """Test User Factory with differents configurations."""

    def test_value_list_factory(self):
        """Default generation."""
        vlf = ValuesListFactory()
        assert vlf.pk

    def test_value_list_with_values_factory(self):
        """Generation with values parmaeters."""
        vlf = ValuesListFactory(values={
            'X': 'A',
            'Y': 'B',
        })
        values = vlf.values.all()
        assert len(values) == 2
        assert values.get(index='X', value="A")
        assert values.get(index='Y', value="B")
