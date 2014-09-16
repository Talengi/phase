from rest_framework import serializers

from notifications.models import Message


class MessageSerializer(serializers.ModelSerializer):
    user = serializers.Field(source='user.email')

    class Meta:
        model = Message
        fields = ('id', 'user', 'body', 'created_on', 'seen')
