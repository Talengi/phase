from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.Field(source='user.email')

    class Meta:
        model = Notification
        fields = ('id', 'user', 'body', 'created_on', 'seen')
