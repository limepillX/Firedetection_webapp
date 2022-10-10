from rest_framework import serializers
from .models import User


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        Model = User
        fields = ('username',)
