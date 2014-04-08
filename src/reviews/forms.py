from django import forms
from django.forms.models import modelform_factory
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.bootstrap import UneditableField

from default_documents.layout import (
    PropertyLayout, DocumentFieldset, UneditableFile
)


class BaseReviewForm(forms.ModelForm):

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False
        helper.layout = Layout(
            DocumentFieldset(
                _('General information'),
                PropertyLayout('document_key'),
                PropertyLayout('title'),
                UneditableField('status'),
                UneditableFile('native_file'),
                UneditableFile('pdf_file'),
            ),
            DocumentFieldset(
                _('Reviewer data'),
                PropertyLayout('current_review_step'),
                UneditableField('review_start_date'),
                UneditableField('review_due_date'),
            ),
            DocumentFieldset(
                _('Reviewers'),
                UneditableField('reviewers'),
                UneditableField('leader'),
                UneditableField('approver'),
            ),
        )
        return helper


def reviewform_factory(*args, **kwargs):
    kwargs.update({
        'fields': ('status', 'review_start_date', 'review_due_date',
                   'reviewers', 'leader', 'approver', 'native_file',
                   'pdf_file'),
        'form': BaseReviewForm,
    })

    return modelform_factory(*args, **kwargs)
