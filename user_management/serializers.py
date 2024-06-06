from rest_framework import serializers
from user_management.models import User

class SignUpSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

class UserSerializer(serializers.ModelSerializer[User]):

    class Meta:
        model = User
        fields = ['name', 'email', 'id']