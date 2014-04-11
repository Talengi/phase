from django.db.models import Q
from rest_framework import viewsets

from accounts.models import User
from api.serializers import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    model = User
    serializer_class = UserSerializer
    paginate_by_param = 'page_limit'

    def get_queryset(self):
        qs = User.objects.all()

        q = self.request.QUERY_PARAMS.get('q', None)
        if q:
            q_name = Q(name__icontains=q)
            q_email = Q(email__icontains=q)
            qs = qs.filter(q_name | q_email)

        return qs
