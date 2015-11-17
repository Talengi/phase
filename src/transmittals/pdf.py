# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.enums import TA_LEFT


tableStyles = TableStyle([
    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
])
styles = getSampleStyleSheet()


def transmittal_to_pdf(revision):
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

    title = 'Phase'
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
