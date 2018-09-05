import os

from django.core.management.base import BaseCommand
from django.db.models import FileField

from documents.models import Document
from documents.fileutils import revision_file_path


class Command(BaseCommand):
    args = '<document> <revision>'
    help = 'Update the native and pdf file names'

    def add_arguments(self, parser):
        parser.add_argument('document_number', type=str)
        parser.add_argument('revision_id', type=str)

    def handle(self, *args, **options):
        document_number = options['document_number']
        revision_id = options['revision_id']

        document = Document.objects.get(document_key=document_number)
        metadata = document.metadata
        revision = metadata.get_revision(revision_id)

        fields = revision._meta.get_fields()
        for field in fields:
            if isinstance(field, FileField):
                f = getattr(revision, field.name)
                if f:
                    self.rename_file(revision, field.name)

    def rename_file(self, revision, field_name):
        self.stdout.write('Renaming {}'.format(field_name))

        field = revision._meta.get_field(field_name)
        f = getattr(revision, field_name)
        initial_name = f.name
        initial_path = f.path

        file_path_function = field.upload_to
        new_name = file_path_function(revision, initial_name)
        new_path = f.storage.path(new_name)

        f.name = new_name
        revision.save()
        os.rename(initial_path, new_path)
        self.stdout.write(self.style.SUCCESS(
            'Renamed\n    {} ->\n    {}'.format( initial_path, new_path)))
