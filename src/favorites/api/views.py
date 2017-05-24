from rest_framework import viewsets
from rest_framework import permissions

from favorites.models import Favorite
from favorites.api.serializers import FavoriteSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    model = Favorite
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
