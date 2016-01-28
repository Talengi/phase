# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import importlib
import os
from io import BytesIO

from django.conf import settings
from django.utils import dateformat
from reportlab.lib import colors, utils
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.platypus.tables import Table, TableStyle


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


class BaseTransmittalPdf(object):
    """
    Pdf generator for transmittals.

    This can be customized on a per organisation basis by writing
    logo settings in COMPANY_LOGOS dict where each item follows this
    pattern: COMPANY_LOGO_XXX where XXX is the organisation trigram.
    Each item is a dict and must define a path to the logo image file and
    optionally a wanted_height, logo_x and logo_y in mm
    (see draw_logo() method).

    It can also be overriden by writing PDF_CONFIGURATION settings
    which will provide dotted paths to custom generators subclassing
    BaseTransmittalPdf.


    """

    def __init__(self, revision):
        self.buff = BytesIO()
        self.styles = getSampleStyleSheet()
        self.width, self.height = A4
        self.revision = revision
        self.document = revision.document
        self.transmittal = revision.metadata
        self.category = self.document.category
        self.revisions = self.transmittal.get_revisions()
        self.trigram = revision.metadata.originator
        self.company_logo_settings = self.get_logo_settings()
        self.build_document()

    def get_logo_settings(self):
        logos_settings = getattr(settings, 'COMPANY_LOGOS', {})
        if type(logos_settings) is not dict:
            raise ImportError('COMPANY_LOGOS must be a dict')

        logo_settings_name = 'COMPANY_LOGO_{}'.format(self.trigram)
        logo_settings = logos_settings.get(logo_settings_name, {})
        if type(logo_settings) is not dict:
            raise ImportError('{} must be a dict'.format(logo_settings_name))
        return logo_settings

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
        self.doc.build(story, onFirstPage=self.build_header,
                       canvasmaker=NumberedCanvas)

    def build_header(self, canvas, doc):
        self.draw_logo(canvas)
        self.draw_title(canvas)
        self.draw_contract_nb_table(canvas)

    def get_table_style(self):
        style = TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])
        return style

    def draw_logo(self, canvas):
        """ Draw the logo on pdf according to following settings:
        logo_path: absolute path to image
        wanted_height: wanted height in mm (optional, default 20 mm)
        logo_x: x coordinate in mm (optional, default 13 mm)
        logo_y: y coordinate in mm (optional, default 55 mm)
        """
        if not self.company_logo_settings:
            return
        # Get logo settings
        logo_path = self.company_logo_settings.get('path', None)
        wanted_height = self.company_logo_settings.get('wanted_height', 20)
        logo_x = self.company_logo_settings.get('x', 13)
        logo_y = self.company_logo_settings.get('y', 55)

        # Sanity check
        if not os.access(logo_path, os.R_OK):
            return

        # get original lgo dimensions to compute ratio
        logo = utils.ImageReader(logo_path)
        width, height = logo.getSize()
        ratio = float(width) / height

        # Compute width according to wanted height
        computed_width = int(wanted_height * ratio)

        # Draw logo
        im = Image(logo_path, computed_width * mm, wanted_height * mm)
        im.drawOn(canvas, *self.coord(logo_x, logo_y))

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
                Paragraph(revision.document.title, body_style),
                Paragraph(revision.name, centered),
                Paragraph(revision.status, centered),
                Paragraph(revision.get_final_return_code(), centered)))
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
        p = Paragraph('Adressee acknowledgment of receipt',
                      self.styles['Normal'])
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


class TransmittalPdf(BaseTransmittalPdf):
    pass


def get_transmittals_pdf_generator(revision):
    """
    Import helper. Takes the organisation trigram name, constructs
    a TRANSMITTALS_PDF_GENERATOR_XXX key in PDF_CONFIGURATION
    settings variable which holds a dotted path, tries to get its value
    then import the class according to the dotted path.
    It returns the imported class.
    """
    pdf_configuration = getattr(settings, 'PDF_CONFIGURATION', {})
    if type(pdf_configuration) is not dict:
        raise ImportError('PDF_CONFIGURATION must be a dict')

    trigram = revision.document.category.organisation.trigram
    pdf_generator_name = 'TRANSMITTALS_PDF_GENERATOR_{}'.format(trigram)
    pdf_generator_path = pdf_configuration.get(pdf_generator_name, None)

    if not pdf_generator_path:
        return TransmittalPdf

    splitted_path = pdf_generator_path.split(".")
    module_path = ".".join(splitted_path[:-1])
    class_str = splitted_path[-1]
    module = importlib.import_module(module_path)
    return getattr(module, class_str)


def transmittal_to_pdf(revision):
    transmittals_pdf_generator = get_transmittals_pdf_generator(revision)
    pdf = transmittals_pdf_generator(revision)
    return pdf.as_binary()
