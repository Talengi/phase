from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route

from notifications.models import Message
from notifications.api.serializers import MessageSerializer


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    model = Message
    serializer_class = MessageSerializer
    paginate_by_param = 'page_limit'

    def get_queryset(self):
        return Message.objects.filter(user=self.request.user)

    @list_route(methods=['post'])
    def mark_as_read(self, request):
        qs = self.get_queryset()
        qs.update(seen=True)
        return Response({'status': 'done'})
