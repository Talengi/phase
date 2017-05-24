import os
import logging

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from privatemedia.fields import PrivateFileField


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Cleanup private storage.

    Since Django 1.3, FileFields instances are not automaticaly deleted upon's
    the mode deletion anymore.

    This is to preserve data integrity in case of transactions rollbacks.

    The drawback is that cleaning file is our responsability.

    This tasks cleans the private storage directory by removing all files that
    are not present in db anymore.

    """
    def handle(self, *args, **options):
        logger.info('Starting private media files cleanup')

        db_files = self.find_files_in_db()
        logger.info('{} files found in db'.format(len(db_files)))

        disk_files = self.find_files_on_disk()
        logger.info('{} files found on disk'.format(len(disk_files)))

        on_disk_only = disk_files - db_files
        in_db_only = db_files - disk_files

        logger.info('{} files found on disk that need cleaning'.format(
            len(on_disk_only)))
        self.clean_files(on_disk_only)

        logger.info('Cleaning done')

        if len(in_db_only) > 0:
            logger.warning('{} files found in db with missing file on disk'.format(
                len(in_db_only)))

    def find_files_in_db(self):
        """Return list of all instances of PrivateFile in db."""
        # Find all model with private file fields
        types = ContentType.objects.all()
        private_fields = tuple()
        for ct in types:
            model_class = ct.model_class()
            fields = model_class._meta.fields
            for field in fields:
                if isinstance(field, PrivateFileField):
                    private_fields += ((model_class, field.name),)
        # Get path for all files in db
        all_files = []
        for Model, field in private_fields:
            # Some migrations seem to introduce null values in
            # OutgoingTransmittal archived_pdf field, so we filter
            # against them
            values = Model.objects \
                .exclude(**{'%s' % field: '', '%s' % field: None}) \
                .values_list(field, flat=True)
            all_files += values

        def prepend_private_root(path):
            return os.path.join(settings.PRIVATE_ROOT, path)

        all_files = list(map(prepend_private_root, all_files))
        return set(all_files)

    def find_files_on_disk(self):
        """Return list of files in private storage dir."""
        root_location = settings.PRIVATE_ROOT
        all_files = []
        for folder, subs, files in os.walk(root_location):
            if len(files) > 0:
                all_files += [os.path.join(folder, f) for f in files]

        return set(all_files)

    def clean_files(self, files):
        """Remove the given files."""
        for f in files:
            self.clean_file(f)

    def clean_file(self, f):
        """Remove a single file."""

        # Clean the path
        path = os.path.abspath(f)

        # Make sure the file we are about to delete
        # really belongs to PRIVATE_ROOT
        if not path.startswith(settings.PRIVATE_ROOT):
            raise RuntimeError('Cannot delete file {}.'.format(path))

        # Check that the file is really a file
        if not os.path.isfile(path):
            raise RuntimeError('{} should be a file.'.format(path))

        # Just in case, make sure we don't delete system files
        if len(path.split('/')) <= 4:
            raise RuntimeError('Something is fishy with file {}. Aborting.'.format(path))

        # Sounds good. Let's delete the file.
        os.remove(path)
