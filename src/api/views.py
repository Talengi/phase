from rest_framework import viewsets

from accounts.models import User
from api.serializers import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    model = User
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()
