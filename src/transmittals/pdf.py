# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.colors import black
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER


tableStyles = TableStyle([
    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
])
styles = getSampleStyleSheet()


def transmittal_to_pdf_old(revision):
    buff = BytesIO()
    document = revision.document
    transmittal = revision.metadata
    category = document.category
    revisions = transmittal.exportedrevision_set.select_related()

    pdf = SimpleDocTemplate(
        buff,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.3 * cm,
        bottomtMargin=2 * cm,
    )
    story = []

    title = category.organisation.name
    story.append(Paragraph(title, styles['Heading1']))

    subtitle = '{}'.format(category)
    story.append(Paragraph(subtitle, styles['Heading3']))

    subsubtitle = 'Document n° {}'.format(document.document_key)
    story.append(Paragraph(subsubtitle, styles['Heading3']))

    story.append(Spacer(0, 1 * cm))

    data = [
        ('From', transmittal.originator),
        ('To', transmittal.recipient),
        ('Contract number', transmittal.contract_number),
        ('Created on', revision.created_on),

    ]
    table = Table(data, hAlign='LEFT')
    table.setStyle(tableStyles)
    story.append(table)

    story.append(Spacer(0, 1 * cm))

    related_docs_table = Table(
        build_revisions_table(revisions),
        colWidths=[None, None, 1 * cm, 1 * cm, 1 * cm])
    related_docs_table.setStyle(tableStyles)
    story.append(related_docs_table)

    pdf.build(story)
    pdf_binary = buff.getvalue()
    buff.close()
    return pdf_binary


def build_revisions_table(revisions):
    style = styles['BodyText']
    style.alignment = TA_LEFT
    style.wordWrap = 'LTR'

    header = (
        'Document',
        'Title',
        'Rev.',
        'St.',
        'RC')
    data = [header]
    for revision in revisions:
        data.append((
            Paragraph(revision.document.document_key, style),
            Paragraph(revision.title, style),
            Paragraph('%s' % revision.revision, style),
            Paragraph(revision.status, style),
            Paragraph(revision.return_code, style)))

    return data


class TransmittalPdf(object):
    def __init__(self, revision):
        self.buff = BytesIO()
        self.c = canvas.Canvas(self.buff, pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.width, self.height = A4
        self.revision = revision
        self.document = revision.document
        self.transmittal = revision.metadata
        self.category = self.document.category
        self.revisions = self.transmittal.exportedrevision_set.select_related()
        self.build_document()

    def build_document(self):
        self._draw_title()
        self._draw_contract_nb_table()
        self._draw_subtitle()

    def _draw_title(self):
        title = self.category.organisation.name
        p = Paragraph(title, self.styles['Title'])
        p.wrapOn(self.c, 120 * mm, 150 * mm)
        p.drawOn(self.c, *self.coord(15, 55))

    def _draw_contract_nb_table(self):
        data = [
            ('Contract NB', self.transmittal.contract_number),
            ('Phase', ''),
        ]
        table = Table(data, hAlign='LEFT', colWidths=[25 * mm, 25 * mm])
        styles = TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])
        table.setStyle(styles)
        table.wrapOn(self.c, 50 * mm, 50 * mm)
        table.drawOn(self.c, *self.coord(145, 55))

    def _draw_subtitle(self):
        style = ParagraphStyle(
            name='trs_style',
            parent=self.styles['Heading2'],
            alignment=TA_CENTER,
            borderWidth=1,
            borderColor=black,
            textTransform='uppercase'
        )
        p = Paragraph('Transmittal sheet', style)
        p.wrapOn(self.c, 130 * mm, 20 * mm)
        p.drawOn(self.c, *self.coord(15, 70))

    def coord(self, x, y, unit=mm):
        """Helper class to computes pdf coordinary

        # http://stackoverflow.com/questions/4726011/wrap-text-in-a-table-reportlab

        """
        x, y = x * unit, self.height - y * unit
        return x, y

    def as_binary(self):
        """Writes the pdf to buffer and returns it as a binary value."""
        self.c.showPage()
        self.c.save()
        pdf_binary = self.buff.getvalue()
        self.buff.close()
        return pdf_binary


def transmittal_to_pdf(revision):
    pdf = TransmittalPdf(revision)
    return pdf.as_binary()
