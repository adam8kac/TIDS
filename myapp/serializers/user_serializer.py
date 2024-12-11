from rest_framework import serializers
from myapp.models.user_model import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "email", "password"]
