# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from io import BytesIO

from django.utils import dateformat

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.enums import TA_CENTER


class NumberedCanvas(canvas.Canvas):
    """Display pagination on bottom of page.

    Shamelessly stolen from here:
    http://stackoverflow.com/questions/1087495/reportlab-page-x-of-y-numberedcanvas-and-images

    """
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.drawRightString(
            200 * mm,
            10 * mm,
            "Page %d of %d" % (self._pageNumber, page_count))


class TransmittalPdf(object):
    def __init__(self, revision):
        self.buff = BytesIO()
        self.styles = getSampleStyleSheet()
        self.width, self.height = A4
        self.revision = revision
        self.document = revision.document
        self.transmittal = revision.metadata
        self.category = self.document.category
        self.revisions = self.transmittal.exportedrevision_set.select_related()
        self.build_document()

    def build_document(self):
        self.doc = SimpleDocTemplate(
            self.buff,
            pagesize=A4,
            leftMargin=13 * mm,
            rightMargin=13 * mm,
            topMargin=13 * mm,
            bottomtMargin=18 * mm)

        story = [
            Spacer(0, 4 * cm),
            self.build_subtitle(),
            Spacer(0, 6 * mm),
            self.build_trs_meta(),
            Spacer(0, 6 * mm),
            self.build_sender_addressee(),
            Spacer(0, 6 * mm),
            self.build_way_of_transmission(),
            Spacer(0, 6 * mm),
            self.build_revisions_table(),
            Spacer(0, 6 * mm),
            self.build_remarks_label(),
            self.build_remarks_field(),
            Spacer(0, 6 * mm),
            self.build_ack_label(),
            self.build_ack_table(),
        ]
        self.doc.build(story, onFirstPage=self.build_header, canvasmaker=NumberedCanvas)

    def build_header(self, canvas, doc):
        self.draw_title(canvas)
        self.draw_contract_nb_table(canvas)

    def get_table_style(self):
        style = TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])
        return style

    def draw_title(self, canvas):
        title = self.category.organisation.name
        p = Paragraph(title, self.styles['Title'])
        p.wrapOn(canvas, 120 * mm, 150 * mm)
        p.drawOn(canvas, *self.coord(13, 55))

    def draw_contract_nb_table(self, canvas):
        data = [
            ('Contract NB', self.transmittal.contract_number),
            ('Phase', ''),
        ]
        table = Table(data, hAlign='LEFT', colWidths=[25 * mm, 25 * mm])
        table.setStyle(self.get_table_style())
        table.wrapOn(canvas, 50 * mm, 50 * mm)
        table.drawOn(canvas, *self.coord(145, 55))

    def build_subtitle(self):
        style = ParagraphStyle(
            name='trs_style',
            parent=self.styles['Heading2'],
            alignment=TA_CENTER,
            borderWidth=1,
            borderColor=colors.black,
            textTransform='uppercase'
        )
        p = Paragraph('Transmittal sheet', style)
        return p

    def build_trs_meta(self):
        date = dateformat.format(
            self.revision.created_on,
            'd/m/Y')
        data = [
            ('Transmittal Number', self.document.document_number),
            ('Issue Date', date),
        ]
        table = Table(data, hAlign='LEFT', colWidths=[70 * mm, 60 * mm])
        table.setStyle(self.get_table_style())
        return table

    def build_sender_addressee(self):
        text = 'Sender: {}<br />Addressee: {}'.format(
            'XXX Sender name',
            'YYY Addressee name'
        )
        p = Paragraph(text, self.styles['Normal'])
        return p

    def build_way_of_transmission(self):
        data = [
            ('Way of transmission', ''),
            ('EDMS', 'X'),
            ('Email', ''),
            ('USB Key', ''),
            ('Post', ''),
            ('Other', ''),
        ]
        table = Table(data, hAlign='LEFT', colWidths=[70 * mm, 20 * mm])
        style = self.get_table_style()
        style.add('SPAN', (0, 0), (1, 0))
        style.add('ALIGN', (0, 0), (0, 0), 'CENTER')
        style.add('ALIGN', (1, 0), (1, -1), 'CENTER')
        table.setStyle(style)
        return table

    def build_revisions_table(self):
        body_style = self.styles['BodyText']

        self.styles.add(ParagraphStyle(
            name='BodyCentered',
            parent=body_style,
            alignment=TA_CENTER,
        ))
        centered = self.styles['BodyCentered']

        header = (
            'Document Number',
            'Title',
            'Rev.',
            'Status',
            'RC')
        data = [header]
        for revision in self.revisions:
            data.append((
                Paragraph(revision.document.document_number, body_style),
                Paragraph(revision.title, body_style),
                Paragraph(revision.name, centered),
                Paragraph(revision.status, centered),
                Paragraph(revision.return_code, centered)))
        table = Table(
            data,
            hAlign='LEFT',
            colWidths=[70 * mm, 75 * mm, 10 * mm, 15 * mm, 10 * mm])
        style = self.get_table_style()
        style.add('ALIGN', (0, 0), (-1, 0), 'CENTER')
        table.setStyle(style)
        return table

    def build_remarks_label(self):
        p = Paragraph('Remarks', self.styles['Normal'])
        return p

    def build_remarks_field(self):
        data = [['\n\n\n']]
        table = Table(data, colWidths=[self.width - 30 * mm])
        table.setStyle(self.get_table_style())
        return table

    def build_ack_label(self):
        p = Paragraph('Adressee acknowledgment of receipt', self.styles['Normal'])
        return p

    def build_ack_table(self):
        data = [
            ('Name:', 'Date:'),
            ('Position:', 'Signature:')
        ]
        table = Table(data, hAlign='LEFT', colWidths=[90 * mm, 90 * mm])
        style = self.get_table_style()
        style.add('INNERGRID', (0, 0), (-1, -1), 0, colors.white)
        table.setStyle(style)
        return table

    def coord(self, x, y, unit=mm):
        """Helper class to computes pdf coordinary

        # http://stackoverflow.com/questions/4726011/wrap-text-in-a-table-reportlab

        """
        x, y = x * unit, self.height - y * unit
        return x, y

    def as_binary(self):
        """Writes the pdf to buffer and returns it as a binary value."""
        pdf_binary = self.buff.getvalue()
        self.buff.close()
        return pdf_binary


def transmittal_to_pdf(revision):
    pdf = TransmittalPdf(revision)
    return pdf.as_binary()
