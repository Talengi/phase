from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

from crispy_forms.helper import FormHelper
from default_documents.layout import DocumentFieldset, FlatRelatedDocumentsLayout

from django.conf import settings


def documentform_factory(model):
    """Gets the given model edition form.

    We are looking for the form class in all installed apps.

    """
    form_class_name = '%sForm' % model.__name__
    apps = settings.INSTALLED_APPS
    DocumentForm = None

    for app in apps:
        try:
            _temp = __import__(
                app + '.forms',
                globals(),
                locals(),
                [form_class_name],
                -1
            )
            DocumentForm = getattr(_temp, form_class_name)
            break
        except (ImportError, AttributeError):
            continue

    else:
        raise ImproperlyConfigured('Cannot find class %s' % form_class_name)

    return DocumentForm


class BaseDocumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.read_only = kwargs.pop('read_only', False)
        self.request = kwargs.pop('request', None)
        self.category = kwargs.pop('category')
        super(BaseDocumentForm, self).__init__(*args, **kwargs)
        self.prepare_form(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = self.build_layout()

        # Document key is automatically generated, this field should not be required
        if 'document_key' in self.fields:
            self.fields['document_key'].required = False

    def build_layout(self):
        raise NotImplementedError('Missing "build_layout" method')

    def prepare_form(self, *args, **kwargs):
        """Perform some common operations."""

        # Init related documents field
        if 'related_documents' in self.fields:
            if self.read_only:
                self.related_documents = DocumentFieldset(
                    _('Related documents'),
                    FlatRelatedDocumentsLayout('related_documents'),
                )
            else:
                self.related_documents = DocumentFieldset(
                    _('Related documents'),
                    'related_documents',
                )

    def clean_native_file(self):
        """Do not allow a PDF file to be uploaded as a native file.

        Checks both the content type and the filename.
        """
        native_file = self.cleaned_data['native_file']
        if native_file is not None and hasattr(native_file, 'content_type'):
            content_type = native_file.content_type
            if content_type == 'application/pdf'\
                    or native_file.name.endswith('.pdf'):
                raise forms.ValidationError(
                    'A PDF file is not allowed in this field.'
                )
        return native_file
