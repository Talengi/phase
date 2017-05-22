# -*- coding: utf-8 -*-


from django.dispatch import Signal


transmittal_created = Signal(providing_args=['document', 'metadata', 'revision'])
transmittal_pdf_generated = Signal(providing_args=['document', 'metadata', 'revision'])
