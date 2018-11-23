from django.test import TestCase

from ..factories import TransmittalFactory


class TransmittalFactoryTests(TestCase):
    """Test TransmittalFactory."""

    def test_transmittal_factory(self):
        """Default generation."""
        trs = TransmittalFactory(status='accepted')
        assert trs.pk
