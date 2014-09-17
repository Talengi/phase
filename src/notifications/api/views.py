from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.authentication import SessionAuthentication

from notifications.models import Message
from notifications.api.serializers import MessageSerializer


# See https://github.com/tomchristie/django-rest-framework/issues/1588
class NoCSRFAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        pass


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    model = Message
    serializer_class = MessageSerializer
    paginate_by_param = 'page_limit'
    authentication_classes = (NoCSRFAuthentication,)

    def get_queryset(self):
        return Message.objects.filter(user=self.request.user)

    @list_route(methods=['post'])
    def mark_as_read(self, request):
        qs = self.get_queryset()
        qs.update(seen=True)
        return Response({'status': 'done'})
