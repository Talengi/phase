from django.test import TestCase

from documents.models import Document


class DocumentTest(TestCase):

    def test_document_number(self):
        """
        Tests that a document number is generated regularly.
        """
        document = Document.objects.create(
            title=u'HAZOP report',
            revision_date='2012-04-20',
            leader=u'Bernard Wallyn',
            approver=u'Pierre Rabeau',
            sequencial_number=4,
            discipline="HSE",
            document_type="REP"
        )
        self.assertEqual(document.document_number,
                         u'FAC09001-FWF-000-HSE-REP-0004')
        self.assertEqual(unicode(document),
                         u'FAC09001-FWF-000-HSE-REP-0004')

    def test_display_fields(self):
        """
        Tests that a document is displayed with a few fields only.
        """
        document = Document.objects.create(
            title=u'HAZOP report',
            revision_date='2012-04-20',
            leader=u'Bernard Wallyn',
            approver=u'Pierre Rabeau',
            sequencial_number=4,
            discipline="HSE",
            document_type="REP",
            revision=3
        )
        self.assertEqual(
            u" | ".join(unicode(field[2]) for field in document.display_fields()),
            (u'FAC09001-FWF-000-HSE-REP-0004 | HAZOP report | IFD | 3 '
             u'| 2012-04-20 | 000 | HSE | REP | 1')
        )
