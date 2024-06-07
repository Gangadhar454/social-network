from rest_framework import serializers
from friendship_management.models import FriendRequest

class FriendRequestValidationSerializer(serializers.Serializer):
    friend_id = serializers.IntegerField(required=True)
    action_choices = (
        ("approve", "approve"),
        ("reject", "reject"),
        ("send_request", "send_request")
    )
    action = serializers.ChoiceField(choices=action_choices, required=True)

class FriendRequestAcceptedSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='requested_to.name', read_only=True)
    user_id = serializers.IntegerField(source='requested_to.id', read_only=True)
    email = serializers.CharField(source='requested_to.email', read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['name', 'user_id', 'email']

class FriendRequestRecievedSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='requested_from.name', read_only=True)
    user_id = serializers.IntegerField(source='requested_from.id', read_only=True)
    email = serializers.CharField(source='requested_from.email', read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['name', 'user_id', 'email']