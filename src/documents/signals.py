# -*- coding: utf-8 -*-


from django.dispatch import Signal


document_form_saved = Signal(
    providing_args=['document', 'metadata', 'revision', 'do_not_rewrite'])
document_created = Signal(providing_args=['document', 'metadata', 'revision'])
document_revised = Signal(providing_args=['document', 'metadata', 'revision'])
revision_edited = Signal(providing_args=['document', 'metadata', 'revision'])
