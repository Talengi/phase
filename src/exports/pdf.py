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


def format_doc_as_pdf(rev):
    buff = BytesIO()
    doc = rev.document
    meta = doc.get_metadata()

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

    subtitle = '{}'.format(doc.category)
    story.append(Paragraph(subtitle, styles['Heading3']))

    subsubtitle = 'Document n° {}'.format(doc.document_key)
    story.append(Paragraph(subsubtitle, styles['Heading3']))

    story.append(Spacer(0, 1 * cm))

    data = [
        ('From', meta.originator),
        ('To', meta.recipient),
        ('Contract number', meta.contract_number),
        ('Created on', rev.created_on),

    ]
    table = Table(data, hAlign='LEFT')
    table.setStyle(tableStyles)
    story.append(table)

    story.append(Spacer(0, 1 * cm))

    related_docs_table = Table(
        build_related_docs_table(rev),
        colWidths=(None, None, 1 * cm, 1 * cm, 1 * cm))
    related_docs_table.setStyle(tableStyles)
    story.append(related_docs_table)

    pdf.build(story)
    pdf_binary = buff.getvalue()
    buff.close()
    return pdf_binary


def build_related_docs_table(rev):
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
    docs = rev.document.get_metadata().related_documents.all()
    for doc in docs:
        data.append((
            Paragraph(doc.document_key, style),
            Paragraph(doc.title, style),
            Paragraph('42', style),
            Paragraph('42', style),
            Paragraph('42', style)))

    return data
