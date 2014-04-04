from django.views.generic import ListView
from django.db.models import Q

from accounts.views import LoginRequiredMixin
from documents.utils import get_all_document_classes
from default_documents.models import ContractorDeliverable
#from reviews.models import ReviewMixin


class DocumentList(LoginRequiredMixin, ListView):
    template_name = 'reviews/document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        user = self.request.user
        q_reviewers = Q(latest_revision__reviewers=user)
        q_approver = Q(latest_revision__approver=user)
        q_leader = Q(latest_revision__leader=user)

        #klasses = get_all_document_classes()
        #documents = []
        #for klass in klasses:
        #    import pdb; pdb.set_trace()
        #    pass

        documents = ContractorDeliverable.objects.filter(q_reviewers|q_approver|q_leader)
        return documents
