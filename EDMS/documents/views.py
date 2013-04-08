from django.views.generic import ListView

from documents.models import Document


class DocumentList(ListView):
    model = Document

    def get_context_data(self, **kwargs):
        context = super(DocumentList, self).get_context_data(**kwargs)
        context['document_active'] = True
        return context
