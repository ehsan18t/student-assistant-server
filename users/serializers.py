from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from .models import *

class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class CustomUserCreateSerializerRetype(CustomUserCreateSerializer):
    class Meta(CustomUserCreateSerializer.Meta):
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'profile_picture', 'user_type']
