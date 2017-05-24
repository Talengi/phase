import logging

from django.core.management.base import BaseCommand, CommandError
from annoying.functions import get_object_or_None

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Generate docs from an imported transmittal.

    This is the same as clicking on "Accept transmittal" on the web gui.

    """
    args = '<transmittal_id>'
    help = 'Create documents from an imported transmittal'

    def handle(self, *args, **options):
        from transmittals.models import Transmittal
        from transmittals.tasks import process_transmittal

        if len(args) != 1:
            error = 'Usage: python manage.py process_transmittal {}'.format(self.args)
            raise CommandError(error)

        transmittal = get_object_or_None(Transmittal, document__document_key=args[0])
        if transmittal is None:
            error = 'Unknown transmittal'
            raise CommandError(error)

        if transmittal.status != 'tobechecked':
            error = 'Wrong transmittal status: {}'.format(transmittal.status)
            raise CommandError(error)

        transmittal.status = 'processing'
        transmittal.save()
        process_transmittal(transmittal.pk)
