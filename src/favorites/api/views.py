from rest_framework import viewsets
from rest_framework import permissions

from favorites.models import Favorite
from favorites.api.serializers import FavoriteSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    model = Favorite
    serializer_class = FavoriteSerializer
    paginate_by_param = 'page_limit'
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def pre_save(self, obj):
        obj.user = self.request.user
