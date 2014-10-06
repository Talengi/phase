from rest_framework import serializers

from favorites.models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.Field(source='user.email')

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'document', 'last_view_date')
