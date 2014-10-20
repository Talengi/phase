from django.test import TestCase
from django.db.models.fields.files import FieldFile

from documents.fields import RevisionFileField
from documents.widgets import PhaseClearableFileInput
from documents.factories import DocumentFactory


class WidgetTests(TestCase):

    def test_clearable_file_widget(self):
        field = RevisionFileField()
        doc = DocumentFactory()
        file_field = FieldFile(doc, field, 'revisions/toto.pdf')
        widget = PhaseClearableFileInput()
        rendered = widget.render('toto.pdf', file_field)
        self.assertTrue('>toto.pdf<' in rendered)
        self.assertTrue('>revisions/toto.pdf<' not in rendered)
